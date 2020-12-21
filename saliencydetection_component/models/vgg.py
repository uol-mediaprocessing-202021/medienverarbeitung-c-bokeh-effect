import torch.nn as nn


def build_vgg16_layers(config, input_channels, batch_norm=False):
    """
    Function to initialize the needed layer for the vgg-network
    :param config: the config parameters
    :param input_channels: the number of input channels for initializing some layers
    :param batch_norm: a flag if batch normalization layers will be used or not
    :return:
    """
    layers = []
    stage = 1
    for i in config:
        if i == 'MaxPool':
            stage += 1
            if stage == 6:  # last MaxPool
                layers += [nn.MaxPool2d(kernel_size=3, stride=1, padding=1)]  # Add Max_Pooling2D-Layer (stride=1)
            else:
                layers += [nn.MaxPool2d(kernel_size=3, stride=2, padding=1)]  # Add Max_Pooling2D-Layer (stride=2)
        else:
            if stage == 6:  # last MaxPool
                conv2d_layers = nn.Conv2d(input_channels, i, kernel_size=3, padding=1)
            else:
                conv2d_layers = nn.Conv2d(input_channels, i, kernel_size=3, padding=1)
            if batch_norm:
                layers += [conv2d_layers, nn.BatchNorm2d(i), nn.ReLU(inplace=True)]
            else:
                layers += [conv2d_layers, nn.ReLU(inplace=True)]
            input_channels = i  # set input channels to number of last output channels
    return layers


class Vgg16(nn.Module):
    """
     Class to realize the vgg-network
     """
    def __init__(self):
        super(Vgg16, self).__init__()
        # a number x indicates a Conv2D-Layer with x output channels, 'M' indicates a Max_Pooling2D-Layer
        self.config = {'tun': [64, 64, 'MaxPool', 128, 128, 'MaxPool', 256, 256, 256, 'MaxPool', 512, 512, 512,
                               'MaxPool', 512, 512, 512, 'MaxPool'],
                       'tun_ex': [512, 512, 512]}
        self.extract_layers = [8, 15, 22, 29]  # [3, 8, 15, 22, 29]  not include conv1 due large memory footprint!
        self.backbone = nn.ModuleList(build_vgg16_layers(self.config['tun'], 3))  # initialize vgg-network

        for i in self.modules():
            if isinstance(i, nn.Conv2d):
                n = i.kernel_size[0] * i.kernel_size[1] * i.out_channels
                i.weight.data.normal_(0, 0.01)
            elif isinstance(i, nn.BatchNorm2d):
                i.weight.data.fill_(1)
                i.bias.data.zero_()

    def load_pretrained_model(self, model):
        """
        Function to load the pretrained weights into the network model
        :param model: the loaded pretrained weights
        """
        self.backbone.load_state_dict(model, strict=False)  # load pretrained model state into nn.ModuleList() !

    def forward(self, x):
        feauture_extractions = []
        for i in range(len(self.backbone)):
            x = self.backbone[i](x)
            if i in self.extract_layers:  # Return the output if it is in the extract array
                feauture_extractions.append(x)
        return feauture_extractions


def print_network(model, name):
    """
    Function to print the network information and the number of parameters
    :param model: the neural netowrk model
    :param name: the name of the model
    """
    num_params = 0
    for p in model.parameters():
        num_params += p.numel()
    print(name)
    print(model)
    print("The number of parameters: {}".format(num_params))
