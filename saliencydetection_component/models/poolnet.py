import torch
from torch import nn  # Basic library for neural network modules
import torch.nn.functional as F  # Functions like Average-Pooling, Dropout etc.

# import backbone networks
from saliencydetection_component.models.vgg import Vgg16
# change imports to the following when train the model
# from models.vgg import Vgg16
# from models.mobilenet import MobileNetV2

# Configuration lists for building the Feature-Aggregation-Module, Fusion-Module and Score-Module with specific input
# and output channels depending on the backbone network outputs
config_vgg_backbone = {'input_channels': [512, 512, 256, 128],  # {C2, C3, C4, C5} are set to {128, 256, 512, 512}!
                       'output_channels': [512, 256, 128, 128],
                       'saliency_input_channels': 128}

# config for Extraction-Blocks: [3, 6, 10, 16]
# config_mobilenet_backbone = {'input_channels': [160, 64, 32, 24],  # {C2, C3, C4, C5} are set to {24, 32, 64, 160}!
#                              'output_channels': [64, 32, 24, 24],
#                              'saliency_input_channels': 24}

# config for Extraction-Blocks: [3, 6, 10, 13]
config_mobilenet_backbone = {'input_channels': [96, 64, 32, 24],  # {C2, C3, C4, C5} are set to {24, 32, 64, 96}!
                             'output_channels': [64, 32, 24, 24],
                             'saliency_input_channels': 24}

config_backbone = {}


def initialize_backbone_pipeline(backbone):
    """
    Function to initialize required the backbone network
    :param backbone: the backbone model of the poolnet; vgg oder mobilenet
    :return: the initialized backbone network and the associated GGM
    """
    if backbone == 'vgg':
        return Vgg16(), GlobalGuidanceModule(backbone)
    elif backbone == 'mobilenet':
        return MobileNetV2(), GlobalGuidanceModule(backbone)


class GlobalGuidanceModule(nn.Module):
    """
    Class to realize the GGM
    """
    def __init__(self, model):
        super(GlobalGuidanceModule, self).__init__()
        if model == 'vgg':
            self.channels = 512
            self.output_channels = [512, 256, 128]
        elif model == 'mobilenet':
            self.channels = 96
            self.output_channels = [64, 32, 24]

        pyramid_pooling_module, global_guidance_flows = [], []
        for i in [1, 3, 5]:  # build the Pyramid Pooling Module (PPM)
            pyramid_pooling_module.append(nn.Sequential(nn.AdaptiveAvgPool2d(i),  # target output 1, 3, 5 squares (1*1)
                                                        nn.Conv2d(self.channels, self.channels, 1, 1, bias=False),
                                                        nn.ReLU(inplace=True)))
        self.pyramid_pooling_module = nn.ModuleList(pyramid_pooling_module)

        self.pyramid_combine_layer = nn.Sequential(nn.Conv2d(self.channels * 4, self.channels, 3, 1, 1, bias=False),
                                                   nn.ReLU(inplace=True))

        for j in self.output_channels:
            global_guidance_flows.append(nn.Sequential(nn.Conv2d(self.channels, j, 3, 1, 1, bias=False),
                                                       nn.ReLU(inplace=True)))
        self.global_guidance_flows = nn.ModuleList(global_guidance_flows)

        for k in self.modules():
            if isinstance(k, nn.Conv2d):
                n = k.kernel_size[0] * k.kernel_size[1] * k.out_channels
                k.weight.data.normal_(0, 0.01)
            elif isinstance(k, nn.BatchNorm2d):
                k.weight.data.fill_(1)
                k.bias.data.zero_()

    def forward(self, x):
        backbone_output = [x[-1]]
        # pass output of backbone trough the PPM and upsample it
        for i in range(len(self.pyramid_pooling_module)):
            backbone_output.append(F.interpolate(self.pyramid_pooling_module[i](x[-1]), x[-1].size()[2:],
                                                 mode='bilinear', align_corners=True))
        # concatenate all backbone_output Tensors together
        pyramid_pooling_output = self.pyramid_combine_layer(torch.cat(backbone_output, dim=1))

        # upsample output from PPM 2x 4x 8x
        global_guidance_flows = []
        for j in range(len(self.global_guidance_flows)):  # scale output of PPM x2, x4 and x8 -> GGFs
            global_guidance_flows.append(self.global_guidance_flows[j]
                                         (F.interpolate(pyramid_pooling_output,
                                                        x[len(self.global_guidance_flows) - 1 - j].size()[2:],
                                                        mode='bilinear', align_corners=True)))

        return global_guidance_flows


class FeatureAggregationLayer(nn.Module):
    """
    Class to realize the FAM-modul
    """
    def __init__(self, channels):
        super(FeatureAggregationLayer, self).__init__()
        self.pooling_downsample_factors = [2, 4, 8]  # pooling factors from the FAM
        pooling_layers, conv2d_layers = [], []

        for i in self.pooling_downsample_factors:
            pooling_layers.append(nn.AvgPool2d(kernel_size=i, stride=i))
            conv2d_layers.append(nn.Conv2d(channels, channels, 3, 1, 1, bias=False))

        self.pooling_layers = nn.ModuleList(pooling_layers)
        self.conv2d_layers = nn.ModuleList(conv2d_layers)
        self.relu = nn.ReLU()

    def forward(self, x):
        x_size = x.size()
        output = x

        for i in range(len(self.pooling_downsample_factors)):
            y = self.conv2d_layers[i](self.pooling_layers[i](x))
            output = torch.add(output, F.interpolate(y, x_size[2:], mode='bilinear', align_corners=True))
        output = self.relu(output)

        return output


class FusionLayer(nn.Module):
    """
    Class to realize the fusion-modul
    """
    def __init__(self, input_channels, output_channels):
        super(FusionLayer, self).__init__()
        self.conv2D_layer = nn.Conv2d(input_channels, output_channels, 3, 1, 1, bias=False)
        self.is_last_fam = False
        if input_channels == config_backbone['input_channels'][-1]:
            self.is_last_fam = True
        else:
            self.conv2D_fuse_layer = nn.Conv2d(output_channels, output_channels, 3, 1, 1, bias=False)

    def forward(self, x, feature_extraction=None, global_guidance_flow=None):
        if self.is_last_fam:
            x = self.conv2D_layer(x)
            return x
        else:
            # prepare for merge, upsample and conv2d x
            x = F.interpolate(x, feature_extraction.size()[2:], mode='bilinear', align_corners=True)
            x = self.conv2D_layer(x)
            # fuse and 3x3 conv
            x = self.conv2D_fuse_layer(torch.add(torch.add(x, feature_extraction), global_guidance_flow))

            return x


class SaliencyMappingLayer(nn.Module):
    """
    Class to realize the score-modul
    """
    def __init__(self, input_channels):
        super(SaliencyMappingLayer, self).__init__()
        # merge the multiple Dimension Tupel to a one dimensional Tensor
        self.saliency_mapping = nn.Conv2d(input_channels, 1, 1, 1)

    def forward(self, x, x_size=None):
        x = self.saliency_mapping(x)
        if x_size is not None:
            # upsample Tensor to original image size
            x = F.interpolate(x, x_size[2:], mode='bilinear', align_corners=True)
        return x


def initialize_layers():
    """
    Function to initialize all the needed layers with the right configuration, e.g. with the right number of input and
    output channels etc.
    :return: the FAM-layers, the fusion-layers and the score-layer
    """
    feature_aggregation_layers, fusion_layers, saliency_mapping_layer = [], [], []

    for i in range(len(config_backbone['input_channels'])):
        feature_aggregation_layers += [FeatureAggregationLayer(config_backbone['input_channels'][i])]
        fusion_layers += [FusionLayer(config_backbone['input_channels'][i], config_backbone['output_channels'][i])]

    saliency_mapping_layer = SaliencyMappingLayer(config_backbone['saliency_input_channels'])

    return feature_aggregation_layers, fusion_layers, saliency_mapping_layer


class PoolNet(nn.Module):
    """
    Class to realize the whole poolnet
    """
    def __init__(self, backbone, global_guidance_modul, feature_aggregation_layers, fusion_layers,
                 saliency_mapping_layer):
        super(PoolNet, self).__init__()
        self.backbone = backbone
        self.global_guidance_modul = global_guidance_modul
        self.feature_aggregation = nn.ModuleList(feature_aggregation_layers)
        self.fusion = nn.ModuleList(fusion_layers)
        self.saliency_mapping = saliency_mapping_layer

    def forward(self, x):
        # pass input through backbone-network and trough the pyramid-pooling-module
        feature_extractions = self.backbone(x)
        global_guidance_flows = self.global_guidance_modul(feature_extractions)

        # reverse all items in the array; begin with last output from backbone
        feature_extractions = feature_extractions[::-1]

        # pass backbone and pyramid_pooling-outputs through feature_aggregation_layers and fusion_layers
        merge = self.feature_aggregation[0](feature_extractions[0])  # first FAM

        for i in range(1, len(feature_extractions)):
            # pass feature trough a fusion layer and then trough the next FAM
            merge = self.fusion[i - 1](merge, feature_extractions[i], global_guidance_flows[i - 1])
            merge = self.feature_aggregation[i](merge)

        merge = self.fusion[-1](merge)  # last "fusion layer" (just conv2D)
        saliency_map = self.saliency_mapping(merge, x.size())

        return saliency_map


def build_model(backbone):
    """
    Function to build the neural network model e.g. the poolnet
    :param backbone: the backbone model of the poolnet; vgg oder mobilenet
    :return: the initialized poolnet model
    """
    global config_backbone
    if backbone == 'vgg':
        config_backbone = config_vgg_backbone
    elif backbone == 'mobilenet':
        config_backbone = config_mobilenet_backbone
    return PoolNet(*initialize_backbone_pipeline(backbone), *initialize_layers())


def weights_init(modul):
    """
    Function to initialize the weights and the bias
    :param modul: the modul from the neural network, e.g. a Conv2D-Layer, a ReLu-Layer etc.
    """
    if isinstance(modul, nn.Conv2d):
        modul.weight.data.normal_(0, 0.01)
        if modul.bias is not None:
            modul.bias.data.zero_()


def print_network(model):
    """
    Function to print the network information and the number of parameters
    :param model: the neural netowrk model
    """
    num_params = 0
    for p in model.parameters():
        num_params += p.numel()
    print(model)
    print("The number of parameters: {}".format(num_params))
