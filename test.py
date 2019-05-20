# -*- coding: utf-8 -*-

import os
import sys
import shutil
import ConfigParser
import codecs

reload(sys)
sys.setdefaultencoding('utf-8')


# 指定忽略的文件名称
igonre_filename_list = ["ignore.txt", ".DS_Store"]
# 指定忽略的文件后缀
igonre_filename_suffix_list = [".mp3", ".lua"]

def filename_is_ignore(filename):
    ''' 判断是否是忽略的文件
    '''
    for item in igonre_filename_list:
        if filename == item:
            return True

    for item in igonre_filename_suffix_list:
        if filename.endswith(item):
            return True

    return False

def copy_dir(path, dest):
    '''复制一个文件夹,可覆盖
    '''

    if not os.path.exists(path):
        return

    #创建目录
    if not os.path.exists(dest):
        os.makedirs(dest)

    items = os.listdir(path)
    for item in items:
        # print("item",item)
        if item.find(".") != 0:
            #避开系统文件
            src = os.path.join(path, item)
            dst = os.path.join(dest, item)
            if os.path.isfile(src):
                if not filename_is_ignore(item):
                    shutil.copyfile(src, dst)
            else:
                #否则如果是个文件夹,递归执行复制函数
                copy_dir(src, dst)

class ConfigParserEx(ConfigParser.ConfigParser):  
    def __init__(self,defaults=None):  
        ConfigParser.ConfigParser.__init__(self,defaults=None)  
    def optionxform(self, optionstr):  
        return optionstr

def load_config(path):
    ''' 读取配置表
    '''
    config = ConfigParserEx()
    config.read(path)

    return config


def is_need_jiami(filePath):
    ''' 判断png是否需要加密
    '''
    if filePath.endswith(".png"):
        plistPath = filePath.replace('.png','.plist')
        if os.path.exists(plistPath):
            return True

    return False

def copy_jiami_file(src, dst, key):
    '''复制一个文件夹,可覆盖
    '''
      
    keyLen = len(key)
    bt = bytearray(key)

    srcFile = open(src, "rb")
    srcData = srcFile.read()
    srcFile.close()

    sbt = bytearray(srcData)

    byteLen = len(sbt)
    maxLen = byteLen
    if maxLen > keyLen :
        maxLen = keyLen
    for i in range(0, maxLen):
        old = sbt[i]
        k = bt[i]
        n = old + k
        if n > 255 :
            sbt[i] = n - 256
        else:
            sbt[i] = n

    tgtFile = open(dst, "wb")
    tgtFile.write(str(sbt))
    tgtFile.close()

def is_need_jiami_png(filePath):
    ''' 判断png是否需要加密
    '''

    if filePath.endswith(".png"):
        plistPath = filePath.replace('.png','.plist')
        if os.path.exists(plistPath):
            return True

    return False


def is_need_jiami_plist(filePath):
    ''' 判断plist是否需要加密
    '''

    if filePath.endswith(".plist"):
        plistPath = filePath.replace('.plist','.png')
        if os.path.exists(plistPath):
            return True

    return False


def copy_jiami_png_file(src, dst, key):
    ''' 拷贝并加密文件。加密方式与密码异或
    '''
      
    keyLen = len(key)
    bt = bytearray(key)

    srcFile = open(src, "rb")
    srcData = srcFile.read()
    srcFile.close()

    sbt = bytearray(srcData)

    byteLen = len(sbt)
    maxLen = byteLen
    if maxLen > keyLen :
        maxLen = keyLen
    for i in range(0, maxLen):
        old = sbt[i]
        k = bt[i]
        n = old + k
        if n > 255 :
            sbt[i] = n - 256
        else:
            sbt[i] = n

    tgtFile = open(dst, "wb")
    tgtFile.write(str(sbt))
    tgtFile.close()


def copy_jiami_plist_file(src, dst, filename):
    ''' 拷贝并修改plist的texture名称
    '''

    shutil.copyfile(src, dst)
    textureName = filename.replace('.plist','.png')
    newTextureName = filename.replace('.plist','.jm')

    old = "<string>" + textureName + "</string>"
    new = "<string>" + newTextureName + "</string>"
    replace_text_by_file(dst, old, new)

def replace_text_by_file(path, old, new):
    '''替换文本文件中的文本
    '''

    sub, name = os.path.split(path)
    temp_path = os.path.join(sub, "temp_" + name)
    if os.path.isfile(temp_path):
        os.remove(temp_path)
    shutil.copy(path, temp_path)
    
    cur_file = codecs.open(path, "w", "utf-8")
    temp_file = codecs.open(temp_path, "r", "utf-8")
    for line in temp_file.readlines():
        cur_file.write(line.replace(old, new))
    cur_file.close()
    temp_file.close()
    
    os.remove(temp_path)


def copy_res_dir(path, dest, key):
    '''复制一个文件夹,可覆盖
    '''

    if not os.path.exists(path):
        return

    #创建目录
    if not os.path.exists(dest):
        os.makedirs(dest)

    items = os.listdir(path)
    for item in items:
        # print("item",item)
        if item.find(".") != 0:
            #避开系统文件
            src = os.path.join(path, item)
            dst = os.path.join(dest, item)
            if os.path.isfile(src):
                if not filename_is_ignore(item):
                    if is_need_jiami_png(src):
                        # 拷贝并加密文件。加密方式与密码异或
                        dst = dst.replace('.png','.jm')
                        copy_jiami_png_file(src, dst, key)
                    elif is_need_jiami_plist(src):
                        # 拷贝并修改plist的texture名称
                        copy_jiami_plist_file(src, dst, item)
                    else:
                        shutil.copyfile(src, dst)
            else:
                #否则如果是个文件夹,递归执行复制函数
                copy_res_dir(src, dst, key)
  
def main():
    # TODO 下面需要替换成自己的目录
    androidPath = os.getenv("GIT_ROOT")+"/roomcard-android"
    luaPath = os.getenv("GIT_ROOT")+"/roomcard-lua"
    # end


    androidBranch = None #不拉取
    # androidBranch = "dev"
    androidAssetsPath = androidPath + "/temp_demo/demo/assets"

    androidDemoPath = androidPath + "/temp_demo/demo"
    antPropertiesPath = androidPath + "/password/roomcard/ant.properties"
    keystorePath = androidPath + "/password/roomcard/jm-demo.keystore"
    
    passwordConfigPath = androidPath + "/password/roomcard/release.config"


    luaBranch = None #不拉取
    # luaBranch = "dev"
    luaAssetsPath = luaPath + ""

    kLuacSign = None
    kLuacKey = None
    kImageKey = None
    configPath = passwordConfigPath
    if os.path.exists(configPath):
        config = load_config(configPath)
        kLuacSign = config.get("password", "luacSign")
        kLuacKey = config.get("password", "luacKey")
        kImageKey = config.get("password", "imageKey")

    print("kLuacSign", configPath, kLuacSign)



    # 需要拷贝且luac的目录。仅处理lua文件
    srcs = ["src", "res"]

    # 需要拷贝的目录
    reses = ["src", "res"]


    # 更新仓库
    if androidBranch != None:
        # update android git 更新打包工具的git
        cmd = "cd " + androidPath + "&& " + "git checkout " + androidBranch + " && git pull"
        print(cmd)
        os.system(cmd)

    if luaBranch != None:
        # update project git 更新项目的git
        cmd = "cd " + luaPath + "&& " + "git checkout " + luaBranch + " && git pull"
        print(cmd)
        os.system(cmd)


    # 移除旧的资源
    for src in srcs:
        androidResPath = androidAssetsPath + "/" + src
        luaResPath = luaAssetsPath + "/" + src
        
        cmd = "rm -rf " + androidResPath
        print(cmd)
        os.system(cmd)

    for res in reses:
        androidResPath = androidAssetsPath + "/" + res
        luaResPath = luaAssetsPath + "/" + res
        
        # 移除旧的资源
        cmd = "rm -rf " + androidResPath
        print(cmd)
        os.system(cmd)
    

    for src in srcs:
        androidResPath = androidAssetsPath + "/" + src
        luaResPath = luaAssetsPath + "/" + src
        

        # copy project resource to pacakge 拷贝项目里面的资源到打包工具
        cmd = "cocos luacompile -s " + luaResPath + " -d " + androidResPath
        if kLuacSign != None:
            cmd = cmd + " -k " + kLuacKey + " -b " + kLuacSign + " --encrypt --disable-compile"

        print(cmd)
        os.system(cmd)


    for res in reses:
        androidResPath = androidAssetsPath + "/" + res
        luaResPath = luaAssetsPath + "/" + res

        # copy project resource to pacakge 拷贝项目里面的资源到打包工具
        print(androidResPath, luaResPath)
        if kImageKey != None:
            copy_res_dir(luaResPath, androidResPath, kImageKey)
        else:
            copy_dir(luaResPath, androidResPath)


    # gen flist 把src和res目录下的所有文件都声称md5写进flist文件里面
    flistPath = os.path.join(androidPath, "genFlist.py")
    cmd = "python " + flistPath + " -s " + androidAssetsPath
    print(cmd)
    os.system(cmd)

    if os.path.exists(antPropertiesPath):
        src = antPropertiesPath
        dst = androidDemoPath + "/ant.properties"
        shutil.copyfile(src, dst)

    if os.path.exists(keystorePath):
        src = keystorePath
        dst = androidDemoPath + "/jm-demo.keystore"
        shutil.copyfile(src, dst)

    # start pacakge 开始打包
    buildPath = androidPath + "/temp_demo/demo/build.xml"
    #执行ant clean
    cmd = "ant clean -f " + buildPath
    print(cmd)
    os.system(cmd)
    
    #执行ant release
    cmd = "ant release -f " + buildPath
    print(cmd)
    os.system(cmd)

    #打开输出文件的目录
    cmd = "adb install -r " + androidPath + "/temp_demo/demo/bin/demo-release.apk"
    print(cmd)
    os.system(cmd)

def  test():
    print("hello")
    pass

if __name__ == '__main__':
    test()

