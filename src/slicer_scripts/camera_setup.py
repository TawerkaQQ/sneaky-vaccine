import numpy as np

# Get the active 3D view
view = slicer.app.layoutManager().threeDWidget(0).threeDView()
cameraNode = view.cameraNode()

distance = 700  # Adjust as needed (in mm)
focalPoint = [0, 0, 0]  # Center of the head, adjust as needed
position = [focalPoint[0], focalPoint[1] - distance, focalPoint[2]]
viewUp = [0, 0, 1]  # Z axis is up

cameraNode.SetPosition(*position)
cameraNode.SetFocalPoint(*focalPoint)
cameraNode.SetViewUp(*viewUp)

# Get coords of camera
pos = [0, 0, 0]
fp = [0, 0, 0]
vu = [0, 0, 0]
cameraNode.GetPosition(pos)
cameraNode.GetFocalPoint(fp)
cameraNode.GetViewUp(vu)
print("Position:", pos)
print("Focal Point:", fp)
print("View Up:", vu)