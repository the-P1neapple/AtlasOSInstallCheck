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

def readYaml(yaml_str, filename):
    try:
        #print(yaml_str)
        tags = set(findall(r'!([\w]+)', yaml_str))
        print("TAGS!\n")
        print(tags)
        print("\n")
        if tags != "":
            for tag in tags:
                print(tag)
                yaml.add_multi_constructor(f"!{tag}", customConstructor)
    except:
        if 'custom.yml' or 'tweaks.yml' in filename:
            pass
        else:
            print("No Tags Found")
            exit(1)
    data = yaml.load(yaml_str, Loader=yaml.FullLoader)
    return data
