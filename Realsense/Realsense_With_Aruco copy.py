import cv2
import cv2.aruco as aruco # pip3 install opencv-contrib-python
import pyrealsense2 as rs # pip3 install pyrealsense2
import numpy as np
from scipy.spatial import distance as dist

#Start realsense pipeline 
pipeline= rs.pipeline()
config= rs.config()

#Eneble device id for more than 1 realsense
#config_1.enable_device('018322070394')

#confing resolution of realsense
rs_w=640
rs_h=480
fps=15

#eneble video stream color and depth
config.enable_stream(rs.stream.depth, rs_w, rs_h, rs.format.z16, fps)
config.enable_stream(rs.stream.color, rs_w, rs_h, rs.format.bgr8, fps)
pipeline.start(config)

#funtion for easily concate video or image
def concat_tile(im_list_2d):
	return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

#name window that show output
cv2.namedWindow("Aruco", cv2.WINDOW_AUTOSIZE)

#aruco funtion to call Ditionary 5x5
aruco_dict = aruco.Dictionary_get(aruco.DICT_4X4_1000)
parameters = aruco.DetectorParameters_create()

parameters.minDistanceToBorder = 0
parameters.adaptiveThreshWinSizeMax = 400

marker = aruco.drawMarker(aruco_dict, 200, 200)
marker = cv2.cvtColor(marker, cv2.COLOR_GRAY2BGR)


showLive=True

#set font of all text
font=cv2.FONT_HERSHEY_SIMPLEX

#main function
while (showLive):
	
	#wait for realsense frame input. if not it will crash out
	frames = pipeline.wait_for_frames()
	depth_frame = frames.get_depth_frame()
	color_frame = frames.get_color_frame()


	depth_image = np.asanyarray(depth_frame.get_data())
	color_image = np.asanyarray(color_frame.get_data())
	

	#rearrange depth_image to color image
	depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.1), cv2.COLORMAP_JET)

	Frame = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)

	#get info of aruco 
	corners, ids, rejected = aruco.detectMarkers(Frame, aruco_dict, parameters=parameters)
	
	#Put text of aruco into image
	for (i, b) in enumerate(corners):

		#get coordinate center of aruco  to put text
		c1 = (b[0][0][0], b[0][0][1])
		c2 = (b[0][1][0], b[0][1][1])
		c3 = (b[0][2][0], b[0][2][1])
		c4 = (b[0][3][0], b[0][3][1])

		x = int((c1[0] + c2[0] + c3[0] + c4[0]) / 4)
		y = int((c1[1] + c2[1] + c3[1] + c4[1]) / 4)
		z = depth_frame.get_distance(int(x),int(y))
  
		data_string = "ID:" + str(ids[i]) + ",(" + str(x) + "," + str(y) + "," + str("{:.2f}".format(z)) + ")"
		frame = cv2.putText(color_image, data_string, (x-30, y), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 255), 2, cv2.LINE_AA)

	#concate color image and depth image
	show=concat_tile([[color_image,depth_colormap]])

	#show output image
	cv2.imshow('TEST', show)
	
	#wait key for exit
	key = cv2.waitKey(10)
	if key & 0xFF == ord('q') or key == 27:
		showLive = False
		break


pipeline.stop()
cv2.destroyAllWindows()
