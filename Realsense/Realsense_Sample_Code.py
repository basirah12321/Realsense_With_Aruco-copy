import pyrealsense2 as rs # pip3 install pyrealsense2
import numpy as np
import cv2

#confing resolution of realsense
rs_w=640
rs_h=480
fps=15

#Start realsense pipeline 
pipeline= rs.pipeline()
config= rs.config()

#Eneble device id for more than 1 realsense
#config_1.enable_device('018322070394')

#eneble video stream color and depth
config.enable_stream(rs.stream.depth, rs_w, rs_h, rs.format.z16, fps)
config.enable_stream(rs.stream.color, rs_w, rs_h, rs.format.bgr8, fps)
config.enable_stream(rs.stream.infrared,1,rs_w, rs_h, rs.format.y8, fps)
config.enable_stream(rs.stream.infrared,2,rs_w, rs_h, rs.format.y8, fps)

pipeline.start(config)

#funtion for easily concate video or image
def concat_tile(im_list_2d):
	return cv2.vconcat([cv2.hconcat(im_list_h) for im_list_h in im_list_2d])

#name window that show output
cv2.namedWindow("TEST", cv2.WINDOW_AUTOSIZE)

showLive=True

#main function
while (showLive):
	
	#wait for realsense frame input. if not, it will crash out
	frames = pipeline.wait_for_frames()
	depth_frame = frames.get_depth_frame()
	color_frame = frames.get_color_frame()
	infrared_frame_one = frames.get_infrared_frame(1)
	infrared_frame_two = frames.get_infrared_frame(2)
	
	depth_image = np.asanyarray(depth_frame.get_data())
	color_image = np.asanyarray(color_frame.get_data())
	infrared_image_one = np.asanyarray(infrared_frame_one.get_data())
	infrared_image_two = np.asanyarray(infrared_frame_two.get_data())

    #rearrange depth_image to color image
	depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.1), cv2.COLORMAP_JET)

	#convert infrared image from gray to bgr
	infrared_image_one=cv2.cvtColor(infrared_image_one, cv2.COLOR_GRAY2BGR)
	infrared_image_two=cv2.cvtColor(infrared_image_two, cv2.COLOR_GRAY2BGR)

    #concate color image and depth image
	show=concat_tile(([color_image,depth_colormap],[infrared_image_one,infrared_image_two]))

	#show output image
	cv2.imshow('TEST', show)

	#wait key for exit
	key = cv2.waitKey(10)
	if key & 0xFF == ord('q') or key == 27:
		showLive = False
		break


pipeline.stop()
cv2.destroyAllWindows()

