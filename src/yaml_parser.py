from re import findall
import yaml


def customConstructor(loader, tag_suffix, node):
    if isinstance(node, yaml.MappingNode):
        try:
            value = list(loader.construct_yaml_map(node))[0]
        except ValueError:
            value = ""
    elif isinstance(node, yaml.ScalarNode):
        value = loader.construct_yaml_str(node)
    elif isinstance(node, yaml.SequenceNode):
        value = loader.construct_yaml_seq(node)
    else:
        raise yaml.constructor.ConstructorError(
            None, None, f'Unsupported node type: {node.id}', node.start_mark)
    name = node.tag[1:].strip(':')
    return {name: value}


def readYamlFile(filename):
    with open(filename, 'r') as f:
        yaml_str = f.read()
    tags = set(findall(r'!([\w]+)', yaml_str))
    for tag in tags:
        yaml.add_multi_constructor(f"!{tag}", customConstructor)
    data = yaml.load(yaml_str, Loader=yaml.FullLoader)
    return data