import os
import glob
import cv2

# Visualize exr -
# https://github.com/Tom94/tev

# exps = ['Angry', 'Happy', 'Neutral', 'Sad', 'Scared']

root = 'E:\Shubhajit_Data\From_SBASAK01-GWY1\FaceDepthSynth'

# FBX file check -

# fbxFiles = []

# for gender in next(os.walk(root))[1]:
#     for id in next(os.walk(os.path.join(root, gender)))[1]:
#         idPath = os.path.join(root, gender, id)
#         for exp in next(os.walk(os.path.join(idPath, 'Simple')))[1]:
#             expPath = os.path.join(idPath, 'Simple', exp)
#             fbxFile = glob.glob(os.path.join(expPath,'*.fbx'))
#             print(fbxFile[0])
#             # if not len(fbxFile) ==1:
#             # # if len(os.listdir(expPath)) == 0:
#             #     print(expPath)

# Depth data check -

root = 'E:\Shubhajit_Data\From_SBASAK01-GWY1\FaceDepthSynth'

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

                            if not (txtCount == exrCount == jpgCount == pngCount):
                                if not txtCount== 2*jpgCount:
                                    print(os.path.join(root, gender, id, bckgnd, scn, exp, hdmvmt))
                                    print(txtCount, exrCount, jpgCount, pngCount)

            else:
                for exp in next(os.walk(os.path.join(root, gender, id, bckgnd)))[1]:
                    for hdmvmt in next(os.walk(os.path.join(root, gender, id, bckgnd, exp)))[1]:

                        txtCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.txt')))
                        exrCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.exr')))
                        pngCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.png')))
                        jpgCount = len(glob.glob(os.path.join(root, gender, id, bckgnd, exp, hdmvmt, '*.jpg')))

                        if not (txtCount == exrCount == jpgCount == pngCount):
                            if not txtCount == 2 * jpgCount:
                                print(os.path.join(root, gender, id, bckgnd, exp, hdmvmt))
                                print(txtCount, exrCount, jpgCount, pngCount)