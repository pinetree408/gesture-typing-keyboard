from rdp import rdp
import numpy as np
import matplotlib.pyplot as plt

#https://www.gakhov.com/articles/find-turning-points-for-a-trajectory-in-python.html

def angle(directions):
    """Return the angle between vectors
    """
    #vec2 = directions[1:]
    #vec1 = directions[:-1]
        
    #norm1 = np.sqrt((vec1 ** 2).sum(axis=1))
    #norm2 = np.sqrt((vec2 ** 2).sum(axis=1))
    #cos = (vec1 * vec2).sum(axis=1) / (norm1 * norm2) 
    xs = directions.T[0]
    ys = directions.T[1]
    #print(norm1, norm2)
    #return np.rad2deg(np.arccos(cos))
    print(directions)
    return np.rad2deg(np.arctan2(xs,ys))


if __name__ == '__main__':
    # Build simplified (approximated) trajectory
    # using RDP algorithm.
    trajectory = [
    [0.2754, -0.7004],
    [0.2754, -0.7004],
    [0.2584, -0.6698],
    [0.2584, -0.6698],
    [0.2482, -0.6664],
    [0.2278, -0.6664],
    [0.2176, -0.6664],
    [0.017, -0.629],
    [0.017, -0.629],
    [-0.1496, -0.5644],
    [-0.2822, -0.5032],
    [-0.2822, -0.5032],
    [-0.561, -0.2924],
    [-0.6392, -0.2142],
    [-0.765, -0.034],
    [-0.8092, 0.051],
    [-0.8092, 0.051],
    [-0.8262, 0.1122],
    [-0.8194, 0.1258],
    [-0.8194, 0.1258],
    [-0.8228, 0.1224],
    [-0.816, 0.1292],
    [-0.7922, 0.153],
    [-0.5576, 0.2856],
    [-0.2686, 0.3196],
    [-0.1836, 0.289],
    [0.0612, 0.068],
    [0.0612, 0.068],
    [0.2788, -0.2584],
    [0.2992, -0.2856],
    [0.3094, -0.3094],
    [0.3128, -0.3128],
    [0.3196, -0.3468],
    [0.3162, -0.3706],
    [0.3094, -0.3638],
    [0.2992, -0.085],
    [0.2992, -0.085],
    [0.3162, 0.391],
    [0.3162, 0.595],
    [0.306, 0.6222],
    [0.2618, 0.68],
    [0.2618, 0.68],
    [0.2618, 0.68],
    [0.2618, 0.68],
    [0.2618, 0.68],
    [0.2618, 0.68],
    [0.2618, 0.68], 
    [-0.7618, 0.68]]

    trajectory = np.array(trajectory)
    simplified_trajectory = rdp(trajectory, epsilon=0.3)
    sx, sy = simplified_trajectory.T
    x, y= trajectory.T

    # Visualize trajectory and its simplified version.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, 'r--', label='trajectory')
    ax.plot(sx, sy, 'b-', label='simplified trajectory')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(loc='best')
        
    # Define a minimum angle to treat change in direction
    # as significant (valuable turning point).
    #minimum angle = 15 degree
    #min_angle = np.pi / 12.0
    min_angle = 15    
    print(simplified_trajectory)
    # Compute the direction vectors on the simplified_trajectory.
    directions = np.diff(simplified_trajectory, axis=0)
    theta = angle(directions)
    print(theta)
    

    # Select the index of the points with the greatest theta.
    # Large theta is associated with greatest change in direction.
    idx = np.where(np.abs(theta) > min_angle)[0] + 1
    print(idx)

    # Visualize valuable turning points on the simplified trjectory.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(sx, sy, 'gx-', label='simplified trajectory')
    ax.plot(sx[idx], sy[idx], 'ro', markersize = 7, label='turning points')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(loc='best')
    plt.show()
