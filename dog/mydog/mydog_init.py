# Import Pidog class
from .mydog import Mydog

# instantiate a Pidog with default parameters
# my_dog = Pidog()

# instantiate a Pidog with custom initialized servo angles
mydog = Mydog(leg_init_angles = [25, 25, -25, -25, 70, -45, -70, 45], 
                head_init_angles = [0, 0, -25], # 
                tail_init_angle= [0]
            )
