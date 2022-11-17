import os
import glob
import subprocess
# import cv2
# import matplotlib.pyplot as plt



# Visualize exr -
# https://github.com/Tom94/tev

# exps = ['Angry', 'Happy', 'Neutral', 'Sad', 'Scared']

# FBX file check -

# root = '/mnt/fastssd/synData/FullBodyModels'

# fbxFiles = []

# for gender in next(os.walk(root))[1]:
#     for id in next(os.walk(os.path.join(root, gender)))[1]:
#         idPath = os.path.join(root, gender, id)
#         for exp in next(os.walk(os.path.join(idPath, 'Simple')))[1]:
#             expPath = os.path.join(idPath, 'Simple', exp)
#             fbxFile = glob.glob(os.path.join(expPath, '*.fbx'))
#             print(fbxFile[0])
#             # if not len(fbxFile) ==1:
#             # # if len(os.listdir(expPath)) == 0:
#             #     print(expPath)
# 72.6 GB in fastssd -> zipped - 66.5 GB

# Depth data check -


os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"


def checkCount(root):
    for gender in next(os.walk(root))[1]:
        for id in next(os.walk(os.path.join(root, gender)))[1]:
            # idPath = os.path.join(root, gender, id)
            for bckgnd in next(os.walk(os.path.join(root, gender, id)))[1]:
                if bckgnd == 'Complex':
                    for scn in next(os.walk(os.path.join(root, gender, id, bckgnd)))[1]:
                        for exp in next(os.walk(os.path.join(root, gender, id, bckgnd,scn)))[1]:
                            for hdmvmt in next(os.walk(os.path.join(root, gender, id, bckgnd, scn, exp)))[1]:

                                txtCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt, '*.txt')))
                                exrCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt, '*.exr')))
                                pngCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt, '*.png')))
                                jpgCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt, '*.jpg')))

                                # pngs = glob.glob(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt, '*.png'))
                                # exrs = glob.glob(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt, '*.exr'))
                                #
                                # pngs.sort()
                                # exrs.sort()
                                #
                                # for p, e in zip(pngs, exrs):
                                #     png = plt.imread(p)
                                #     exr = cv2.imread(e,  cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
                                #     exr_plt = exr/5.0
                                #     print(png, exr)

                                # pngFiles = glob.glob(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt, 'depth*.png'))
                                #
                                # for f in pngFiles:
                                #     os.remove(f)

                                if not (txtCount == exrCount == jpgCount == pngCount):
                                    # if txtCount== 2*jpgCount:
                                    print(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt))
                                    print(txtCount, exrCount, jpgCount, pngCount)

                else:
                    for exp in next(os.walk(os.path.join(root, gender, id, bckgnd)))[1]:
                        for hdmvmt in next(os.walk(os.path.join(root, gender, id, bckgnd, exp)))[1]:

                            txtCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.txt')))
                            exrCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.exr')))
                            pngCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.png')))
                            jpgCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.jpg')))

                            # pngFiles = glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, 'depth*.png'))
                            #
                            # for f in pngFiles:
                            #     os.remove(f)

                            if not (txtCount == exrCount == jpgCount == pngCount):
                                # if txtCount == 2 * jpgCount:
                                #     headposeFiles = glob.glob(os.path.join(root, gender, id, bckgnd,
                                #                                            exp, hdmvmt, 'headpose*.txt'))
                                #
                                #     for f in headposeFiles:
                                #         os.remove(f)

                                print(os.path.join(root, gender, id, bckgnd, exp, hdmvmt))
                                print(txtCount, exrCount, jpgCount, pngCount)


def manipulateForPaper(root):
    for gender in next(os.walk(root))[1]:
        for id in next(os.walk(os.path.join(root, gender)))[1]:
            # idPath = os.path.join(root, gender, id)
            for bckgnd in next(os.walk(os.path.join(root, gender, id)))[1]:
                if bckgnd == 'Textured':
                    path = os.path.join(root, gender, id, 'Textured')
                    print(path, ' : ', os.path.exists(path))

                    cmd = "rm -r " + path
                    # print(cmd)
                    p = subprocess.call(cmd, shell=True)


# Headpose data check -

# root = '/mnt/fastssd/synData/HeadPoseSynth'
# totalTxtCount = 0
# for bckgnd in next(os.walk(root))[1]:
#     for gender in next(os.walk(os.path.join(root, bckgnd)))[1]:
#         for id in next(os.walk(os.path.join(root, bckgnd, gender)))[1]:
#             txtCount = len(glob.glob(os.path.join(root, bckgnd, gender, id, '*.txt')))
#             jpgCount = len(glob.glob(os.path.join(root, bckgnd, gender, id, '*.jpg')))
#             # print(os.path.join(root, bckgnd, gender, id))
#             # print(txtCount, jpgCount)
#             totalTxtCount += txtCount
#             # if not txtCount == jpgCount:
#             #     print(os.path.join(root, bckgnd, gender, id))
# print('Total text count : ', totalTxtCount)
# 'TexturedBackground' : 92575
# 'RealBackground' : 268567
# total : 367142
# 138 GB in fastssd


def get_file_count_DIB(root):
    exrtotal=0
    jpgtotal=0
    txttotal=0
    folders = [x[0] for x in os.walk(root)]
    pos = ['HeadRot', 'HeadCameraRotTran', 'CameraTran']
    for folder in folders:
        if any(element in folder for element in pos):
            txtCount = len(glob.glob(os.path.join(folder, '*.txt')))
            jpgCount = len(glob.glob(os.path.join(folder, '*.jpg')))
            exrcount = len(glob.glob(os.path.join(folder, '*.exr')))
            exrtotal += exrcount
            jpgtotal += jpgCount
            txttotal += txtCount

            print(folder, ':', txtCount, exrcount, jpgCount)

    print('exr: ', exrtotal, ' jpg: ', jpgtotal, ' txt: ', txttotal)

# total exr:  37670  jpg:  37670  txt:  37670
# exr:  6650  jpg:  6650  txt:  6650
# exr:  6860  jpg:  6860  txt:  6860


if __name__ == '__main__':
    root = '/mnt/fastssd/synData/FaceDepthSynth/For_Paper/female_data_part1'
    get_file_count_DIB(root)