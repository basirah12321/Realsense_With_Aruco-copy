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

align_to = rs.stream.color  # align_to  Is the stream type for which the depth frame is scheduled to be aligned
align = rs.align(align_to)  # rs.align  Align the depth frame with other frames
#funtion for easily concate video or image

#chomehhhh

def get_aligned_images():
    frames = pipeline.wait_for_frames()  # Wait for image frame , Get the frameset of color and depth
    aligned_frames = align.process(frames)  # Get alignment frame , Align the depth box with the color box

    aligned_depth_frame = aligned_frames.get_depth_frame()  # Gets the in the alignment frame depth frame
    aligned_color_frame = aligned_frames.get_color_frame()  # Gets the in the alignment frame color frame

    ####  Get camera parameters  ####
    depth_intrin = aligned_depth_frame.profile.as_video_stream_profile().intrinsics  # Get the depth parameter （ Pixel coordinate system to camera coordinate system will use ）
    color_intrin = aligned_color_frame.profile.as_video_stream_profile().intrinsics  # Get camera internal parameters

    ####  take images To numpy arrays ####
    img_color = np.asanyarray(aligned_color_frame.get_data())  # RGB chart
    img_depth = np.asanyarray(aligned_depth_frame.get_data())  # Depth map （ Default 16 position ）

    return color_intrin, depth_intrin, img_color, img_depth, aligned_depth_frame

'''  Obtain the 3D coordinates of random points  '''
	


point = (400, 300)
def show_distance(event, x, y, args, params):
    global point
    point = (x, y)

cv2.namedWindow('TEST')
cv2.setMouseCallback('TEST',show_distance)

def get_3d_camera_coordinate(depth_pixel, aligned_depth_frame, depth_intrin):

    x = depth_pixel[0]
    y = depth_pixel[1]
    dis = aligned_depth_frame.get_distance(x, y)  # Get the depth corresponding to the pixel
    # print ('depth: ',dis) #  The unit of depth is m
    camera_coordinate = rs.rs2_deproject_pixel_to_point(depth_intrin, depth_pixel, dis)
    #print ('camera_coordinate: ',camera_coordinate)
    
    return dis, camera_coordinate




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
#while True:
    
	
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
 
	
 	# Get the alignment image and camera parameters

 
	#Put text of aruco into image
	for (i, b) in enumerate(corners):

		color_intrin, depth_intrin, img_color, img_depth, aligned_depth_frame = get_aligned_images()
		dis, camera_coordinate = get_3d_camera_coordinate(point, aligned_depth_frame, depth_intrin)
		cv2.circle(img_color, point, 4, (0, 0, 255))
  		
    	
  
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
  
  
		#print('depth: ', dis*100)
		#print('camera_coordinate: ', camera_coordinate)
		print(str(ids[i]))
		
		
  
		cv2.circle(img_color, point, 4, (0, 0, 255))
		cv2.imshow('Realsense', img_color)

	#concate color image and depth image
	show=concat_tile([[color_image,depth_colormap]])

	#show output image
	cv2.imshow('TEST', show)
	
	#wait key for exit
	key = cv2.waitKey(10)
	if key & 0xFF == ord('q') or key == 27:
		showLive = False
		break


#pipeline.stop()
cv2.destroyAllWindows()
