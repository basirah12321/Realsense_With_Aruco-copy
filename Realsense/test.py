# -*- coding: utf-8 -*-
import pyrealsense2 as rs
import numpy as np
import cv2

'''  Set up  '''
pipeline = rs.pipeline()  # Define the process pipeline, Create a pipe
config = rs.config()  # Define configuration config
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)  # To configure depth flow
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 15)  # To configure color flow

# config.enable_stream(rs.stream.depth, 848, 480, rs.format.z16, 90)
# config.enable_stream(rs.stream.color, 848, 480, rs.format.bgr8, 30)

# config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
# config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

pipe_profile = pipeline.start(config)  # streaming The flow begins

#  Create aligned objects with color Flow alignment
align_to = rs.stream.color  # align_to  Is the stream type for which the depth frame is scheduled to be aligned
align = rs.align(align_to)  # rs.align  Align the depth frame with other frames

'''  Get the alignment image frame and camera parameters  '''


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

# Create mouse event
point = (400, 300)
def show_distance(event, x, y, args, params):
    global point
    point = (x, y)

# Initialize Camera Intel Realsense


# Create mouse event
cv2.namedWindow('RealSence')
cv2.setMouseCallback('RealSence',show_distance)



def get_3d_camera_coordinate(depth_pixel, aligned_depth_frame, depth_intrin):

    x = depth_pixel[0]
    y = depth_pixel[1]
    dis = aligned_depth_frame.get_distance(x, y)  # Get the depth corresponding to the pixel
    # print ('depth: ',dis) #  The unit of depth is m
    camera_coordinate = rs.rs2_deproject_pixel_to_point(depth_intrin, depth_pixel, dis)
    #print ('camera_coordinate: ',camera_coordinate)
    return dis, camera_coordinate


if __name__ == "__main__":
    while True:
        '''  Get the alignment image frame and camera parameters  '''
        color_intrin, depth_intrin, img_color, img_depth, aligned_depth_frame = get_aligned_images()  # Get the alignment image and camera parameters


        # Show distance for a specific point

        #distance = depth_frame[point[1], point[0]]


        '''  Obtain the 3D coordinates of random points  '''
        depth_pixel =(320,240)# Set random points , Take the center point of the camera as an example
        dis, camera_coordinate = get_3d_camera_coordinate(point, aligned_depth_frame, depth_intrin)
        print('depth: ', dis*100)  # The unit of depth is mm
        print('camera_coordinate: ', camera_coordinate)

        '''  Display images and annotations  '''
        ####  Mark random points and their coordinates in the diagram  ####

        cv2.circle(img_color, point, 4, (0, 0, 255))

        #cv2.circle(img_color, (320,240), 8, [255, 0, 255], thickness=-1)
        cv2.putText(img_color, "Dis:" + str(dis*100) + " cm", (40, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, [0, 0, 255])
        cv2.putText(img_color, "X:" + str(100*camera_coordinate[0]) + " cm", (80, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    [255, 0, 0])
        cv2.putText(img_color, "Y:" + str(100*camera_coordinate[1]) + " cm", (80, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    [255, 0, 0])
        cv2.putText(img_color, "Z:" + str(100*camera_coordinate[2]) + " cm", (80, 160), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    [255, 0, 0])

        ####  display frame  ####
        #cv2.circle(img_color, point, 15, (0, 0, 255))
        cv2.imshow('RealSence', img_color)
        key = cv2.waitKey(1)