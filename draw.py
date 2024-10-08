import globals as gl
import os
import pandas as pd
from anytree import Node, RenderTree, ContRoundStyle
from anytree.exporter import JsonExporter
from shutil import copyfile, copytree


def draw_from_filter(path):
    df = pd.read_csv(os.path.join(path, 'df_filtered.csv'), sep=";", names=gl.COLS_DF)

    path_lists = df['fullpath'].str.split('/').values.tolist()

    info_lists = df[['deep', 'hsa_son', 'url_kegg_son', 'isoform', 'relation',
                     'type_rel', 'pathway_of_origin', 'occurrences']].values.tolist()

    tree = list_to_anytree(path_lists, info_lists)

    export_tree_in_txt(tree, path)


def draw_from_analysis(gene_info, path):
    df = pd.read_csv(os.path.join(path, 'df_resulted.csv'), sep=";", names=gl.COLS_DF)

    path_lists = df['fullpath'].str.split('/').values.tolist()

    info_lists = df[['deep', 'hsa_son', 'url_kegg_son', 'isoform', 'relation',
                     'type_rel', 'pathway_of_origin', 'occurrences']].values.tolist()

    tree = list_to_anytree(path_lists, info_lists, gene_info)

    path_tree = os.path.join(path, 'demo_radialtree')
    #os.makedirs(path_tree)

    export_tree_in_json(tree, path_tree)

    export_tree_in_txt(tree, path_tree)

    copyfile(os.path.join(path, 'index.html'), os.path.join(path_tree, 'index.html'))
    copyfile(os.path.join(path, 'help.html'), os.path.join(path_tree, 'help.html'))
    copytree(os.path.join(path, 'assets'), os.path.join(path_tree, 'assets'))


def list_to_anytree(lst, lst2, info_root=None):
    root_name = lst[0][0]

    if info_root is None:
        root_node = Node(name=root_name)
    else:
        root_node = Node(name=root_name, hsa=info_root[0], url=info_root[2], info='nan',
                         occurrences=0, deep=0, isoforms='nan')

    for branch, i in zip(lst, lst2):
        parent_node = root_node
        assert branch[0] == parent_node.name

        for cur_node_name in branch[1:]:
            cur_node = next(
                (node for node in parent_node.children if node.name == cur_node_name),
                None,
            )
            if cur_node is None:
                cur_node = Node(name=cur_node_name, hsa=i[1], url=i[2], info=concat_info(i[4], i[5], i[6]),
                                occurrences=i[7], deep=i[0], isoforms=str(i[3]), parent=parent_node)
            parent_node = cur_node
    return root_node


def concat_info(rel, type_rel, patwhay):
    rel_arr = rel.split('§§')
    type_rel_arr = type_rel.split('§§')
    patwhay_arr = patwhay.split('§§')

    str_info = ' - '.join([f'{c} | {a} | {b}' for a, b, c in zip(rel_arr, type_rel_arr, patwhay_arr)])
    return str_info


def export_tree_in_json(tree, path):
    f = open(os.path.join(path, 'data-flare.json'), 'w')
    exporter = JsonExporter(indent=4)
    exporter.write(tree, f)


def export_tree_in_txt(tree, path):
    tree_txt = ''
    for pre, _, node in RenderTree(tree, style=ContRoundStyle()):
        tree_txt += f'{pre}{node.name}\n'

    with open(os.path.join(path, 'tree.txt'), 'w') as f:
        f.write(tree_txt)
