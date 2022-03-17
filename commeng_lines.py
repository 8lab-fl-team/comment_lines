import os
# 代码所在目录
#FILE_PATH = '/Users/wangkai/Desktop/ppcp/ppcp'
FILE_PATH = '/Users/wangkai/Desktop/ppcn-web/ppcn'
#FILE_PATH = '/Users/wangkai/Desktop/FL-Scheduler/python'

file_list=[]
#   将项目下所有的.py文件目录输出
for root,dirs,files in os.walk(FILE_PATH):
        for file in files:
            #获取文件路径
            s=os.path.join(root,file)
            if os.path.splitext(s)[1] == '.py':
                 file_list.append(s)
def analyze_code(codefilesource):
    '''
        打开一个py文件，统计其中的代码行数，包括空行和注释
        返回含该文件代码行数，注释行数，空行数的列表
    '''
    with open(codefilesource,'r',encoding='utf-8') as f:
        code_lines = 0       #代码行数
        comment_lines = 0    #注释行数
        blank_lines = 0      #空白行数  内容为'\n',strip()后为''
        is_comment = False
        start_comment_index = 0 #记录以'''或"""开头的注释位置
        for index,line in enumerate(f,start=1):
            line = line.strip() #去除开头和结尾的空白符

        #判断多行注释是否已经开始 
            if not is_comment:
                if line.startswith("'''") or line.startswith('"""'):
                    is_comment = True
                    start_comment_index = index

                #单行注释
                elif line.startswith('#'):
                    comment_lines += 1
                #空白行
                elif line == '':
                    blank_lines += 1
                #代码行
                else:
                    code_lines += 1


            #多行注释已经开始
            else:
                if line.endswith("'''") or line.endswith('"""'):
                    is_comment = False
                    comment_lines += index - start_comment_index + 1
                else:
                    pass

    print("注释:%d" % comment_lines)
    print("空行:%d" % blank_lines)
    print("代码:%d" % code_lines)
   

    return [code_lines, comment_lines, blank_lines]


def run():
    total_lines, total_comment_lines, total_blank_lines=0,0,0
    for i in file_list:
        print(i)
        line = analyze_code(i)
        total_lines, total_comment_lines, total_blank_lines = total_lines + line[0], total_comment_lines + line[1], total_blank_lines + line[2]

    print ("总代码行数：", total_lines)
    print ("总注释行数：", total_comment_lines, "占%0.2f%%" % (total_comment_lines*100.0/total_lines))
    print ("总空行数：  ", total_blank_lines, "占%0.2f%%" % (total_blank_lines*100.0/total_lines))
    print (f"注释率 :{total_comment_lines/total_lines*100}%")
if __name__ == '__main__':
    run()