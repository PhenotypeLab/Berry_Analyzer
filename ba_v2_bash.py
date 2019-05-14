from ba_v2 import analyzer, organs
from os import listdir
import sys, getopt
from pathlib import Path

def bash(path_to_photos, output_dir = None, color_folder=None, organ='bayas', keywords=[]):
    if output_dir!=None:
        output_dir = Path(output_dir)
    path_to_photos=Path(path_to_photos)
    if output_dir!=None:
        final = open(output_dir / 'report.tsv', 'w')
        final.close()
    counter=0
    if output_dir == None:
        screen_result = ''
    for n in listdir(path_to_photos):
        if 'report.tsv' in n:
            continue
        print(n, end=' ')
        if n[-4:] != '.png' or n[0] == '.' or '_watcher.png' in n:
            print('not valid file')
            continue
        keycheck = False
        if keywords != None:
            for k in keywords:
                if k in n:
                    keycheck = True
                    break
            if not keycheck:
                print('no keyword found')
                continue
        #print(path_to_photos+n, output_dir+n)
        try:
            if output_dir!=None:
                data=analyzer(url=(path_to_photos/n).as_posix(), url_output=output_dir.as_posix(), color_folder=color_folder, json_data=False, organ=organ)
            else:
                data = analyzer(url=(path_to_photos / n).as_posix(), url_output=output_dir, color_folder=color_folder, json_data=False, organ=organ)
        except:
            print('this image can not be analyzed')
            continue
        if counter == 0:
            if output_dir!=None:
                #header=['file']+data[0]
                final = open(output_dir / 'report.tsv', 'a')
                final.write('\t'.join(['file']+data[0]) + '\n')
                final.close()

            else:
                screen_result+='\t'.join(['file']+data[0])+'\n'
            counter += 1
        if output_dir!=None:
            final = open(output_dir / 'report.tsv', 'a')
            final.write('\n'.join(['\t'.join(list(map(str, [n]+d))) for d in data[1:]]) + '\n')
            final.close()
        else:
            screen_result+='\n'.join(['\t'.join(list(map(str, [n]+d))) for d in data[1:]]) + '\n'
        print('ok')
    print('done')
    if output_dir!=None:
        return '\nThe output files has been generated in ' + output_dir.as_posix()
    else:
        return '\n'+screen_result
#print(bash('D:/downloads/postcosecha', keywords=['bayas']))

def main(argv):
    input_dir=''
    output_dir=None
    color_dir=None
    organ=None
    keywords=None
    try:
        opts, args = getopt.getopt(argv,"hi:o:c:g:k:",["input_dir=", 'output_dir=', 'color_dir=', 'organ=', 'keywords='])
    except getopt.GetoptError:
        print('-i <image(s) directory> -o <data output directory> -c <color templates directory> -g <organ> -k <keywords>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('-i <input image(s) directory>')
            sys.exit()
        elif opt in ("-i", "--input_dir"):
            input_dir = arg
        elif opt in ("-o", "--output_dir"):
            output_dir = arg
        elif opt in ("-c", "--color_dir"):
            color_dir = arg
        elif opt in ("-g", "--organ"):
            organ = arg
        elif opt in ("-k", "--keywords"):
            keywords = arg.split(' ')
        else:
            print(opt, arg)
    if organ==None or organ not in organs:
        print('You must specify a valid organ under the flag -g')
        print('Organ options:')
        print('- '+'\n- '.join(organs))
        sys.exit(2)
    print(bash(path_to_photos=input_dir, output_dir=output_dir, color_folder=color_dir, organ=organ, keywords=keywords))
    sys.exit()

if __name__ == "__main__":
   main(sys.argv[1:])