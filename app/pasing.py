import os
import re
from typing import List
import yaml

uniq_dir = os.getcwd()

def findFile(current_dir:str, target_name:str) -> str:
    target_dir = ""
    files = os.listdir(current_dir)
    for file in files:
        if file == target_name:
            return current_dir + "/" + file
        elif os.path.isdir(current_dir + "/" + file):
            temp_dir = findFile(current_dir + "/" + file, target_name)
            if temp_dir != "":
                target_dir = temp_dir
    return target_dir
    
def findFileList(current_dir:str, target_name:str) -> List[str]:
    target_list = []
    files = os.listdir(current_dir)
    for file in files:
        if file == target_name:
            target_list.append(current_dir + "/" + file) 
        elif os.path.isdir(current_dir + "/" + file):
            temp_list = findFileList(current_dir + "/" + file, target_name)
            target_list.extend(temp_list)
    return target_list

def findPthList(current_dir:str) -> List[str]:
    target_list = []
    files = os.listdir(current_dir)
    for file in files:
        if ".pth" in file:
            target_list.append(current_dir + "/" + file) 
        elif os.path.isdir(current_dir + "/" + file):
            temp_list = findPthList(current_dir + "/" + file)
            target_list.extend(temp_list)
    return target_list


def findConf(nowdir:str) -> str:
    conf_path = findFileList(nowdir, "config.yaml")
    rconf = ""
    for i in conf_path:
        if 'logdir' not in i:
            rconf = i
    return rconf

def findBestPth(nowdir:str) -> str:
    pth_path_list = findPthList(nowdir)
    pth_name_list = []
    bestIdx = 0
    count = 0
    for pth_path in pth_path_list :
        temp_name = pth_path.split('/')
        pth_name_list.append(temp_name[-1])
    # print(pth_name_list)
    # print(pth_path_list)
    for i in range(0, len(pth_name_list)):
        file_size = os.path.getsize(pth_path_list[i])
        if "train.total_count.best" in pth_name_list[i] and file_size > 10000000 :
            bestIdx = i
            count = 10000000000
        elif "epoch" in pth_name_list[i]:
            numbers = re.findall(r'\d+', pth_name_list[i])
            this_num = int(numbers[0])
            if this_num > count:
                count = this_num
                bestIdx = i
    if len(pth_path_list) == 0 :
        return None
    return pth_path_list[bestIdx]

def findTrainShape(nowdir:str) -> List[str]:
    """
    [text_shape.phn, speech_shape]
    """
    path_list = []
    t_list = findFileList(nowdir, "text_shape.phn")
    s_list = findFileList(nowdir, "speech_shape")
    for i in t_list:
        if 'valid' in i and 'logdir' not in i:
            path_list.append(i)

    for i in s_list:
        if 'valid' in i and 'logdir' not in i:
            path_list.append(i)

    return path_list

def findValidShape(nowdir:str) -> List[str]:
    """
    [text_shape.phn, speech_shape]
    """
    path_list = []
    t_list = findFileList(nowdir, "text_shape.phn")
    s_list = findFileList(nowdir, "speech_shape")

    for i in t_list:
        if 'valid' in i and 'logdir' not in i:
            path_list.append(i)

    for i in s_list:
        if 'valid' in i and 'logdir' not in i:
            path_list.append(i)
      
    return path_list

def findFeatsConf(nowdir:str) -> List[str]:
    """
    [feats_stats.npz]
    """
    path_list = []
    n_list = findFileList(nowdir, "feats_stats.npz")

    for i in n_list:
        if 'train' in i and 'logdir' not in i:
            path_list.append(i)
      
    return path_list

def findPitchConf(nowdir:str) -> List[str]:
    """
    [feats_stats.npz]
    """
    path_list = []
    n_list = findFileList(nowdir, "pitch_stats.npz")

    for i in n_list:
        if 'train' in i and 'logdir' not in i:
            path_list.append(i)
      
    return path_list

def findEnergyConf(nowdir:str) -> List[str]:
    """
    [feats_stats.npz]
    """
    path_list = []
    n_list = findFileList(nowdir, "energy_stats.npz")

    for i in n_list:
        if 'train' in i and 'logdir' not in i:
            path_list.append(i)
      
    return path_list


def updateConf(nowdir):
    status = True
    confPath = findConf(nowdir)
    print("start change conf")
    with open(confPath, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
        print("conf load complete")

    # train shape 부분 고치기
    ts_list = findTrainShape(nowdir)
    #print(ts_list)
    if 'train_shape_file' in config:
        for i, path in enumerate(config['train_shape_file']):
            if "text_shape.phn" in path:
                config['train_shape_file'][i] = ts_list[0]
                print(ts_list[0])
            elif "speech_shape" in path:
                config['train_shape_file'][i] = ts_list[1]
                print(ts_list[1])
    else :
        print("train_shape_fail")

    # valid shape 부분 고치기
    vs_list = findTrainShape(nowdir)
    #print(vs_list)
    if 'valid_shape_file' in config:
        for i, path in enumerate(config['valid_shape_file']):
            if "text_shape.phn" in path:
                config['valid_shape_file'][i] = vs_list[0]
                print(vs_list[0])
            elif "speech_shape" in path:
                config['valid_shape_file'][i] = vs_list[1]
                print(vs_list[1])
    else :
        print("valid_shape_fail")

    # 기타 고치기
    oneconf = findFeatsConf(nowdir)[0]
    #print(oneconf)
    if 'normalize_conf' in config and 'stats_file' in config['normalize_conf']:
        config['normalize_conf']['stats_file'] = oneconf
        print(oneconf)
    else :
        print("feat_fail")
        if 'normalize_conf' not in config:
            print('normalize_conf is not')
        if 'stats_file' not in config['normalize_conf']:
            print('stats_file is not')
        print("")
    
    oneconf = findPitchConf(nowdir)[0]
    #print(oneconf)
    if 'pitch_normalize_conf' in config and 'stats_file' in config['pitch_normalize_conf']:
        config['pitch_normalize_conf']['stats_file'] = oneconf
        print(oneconf)
    else :
        print("pitch_fail")

    oneconf = findEnergyConf(nowdir)[0]
    #print(oneconf)
    if 'energy_normalize_conf' in config and 'stats_file' in config['energy_normalize_conf']:
        config['energy_normalize_conf']['stats_file'] = oneconf
        print(oneconf)
    else :
        print("energy_fail")

    # conf dump
    with open(confPath, 'w', encoding='utf-8') as file:
        yaml.dump(config, file, allow_unicode=True, default_flow_style=False)

    return status

if __name__ == "__main__":
    updateConf(uniq_dir)
    print(findConf(uniq_dir))

    # print(findBestPth(uniq_dir))
    # print(findFile(uniq_dir, "feats_stats.npz"))
    # print(findTrainShape(uniq_dir))
    # print(findEnergyConf(uniq_dir))
