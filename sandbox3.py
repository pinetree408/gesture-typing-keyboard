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

def get_corner_angle_sequence_from_position(positions):
    #print(positions)
    #positions = self.normalize(positions)
    print(positions)
    #positions = np.diff(positions, axis= 0)
    #np.insert(positions, 0, 0)
    #print(positions)
    simplified_trajectory = rdp(positions, epsilon=0.3)
    #minimum angle = 15 degree
    #print(simplified_trajectory)
    # Compute the direction vectors on the simplified_trajectory.

    simplified_trajectory = np.array(simplified_trajectory)
    xs = simplified_trajectory.T[0]
    ys = simplified_trajectory.T[1]



    angle_sequence= np.rad2deg(np.arctan2(xs,ys))
    visualize_path(positions, simplified_trajectory, angle_sequence)
    #idx = np.where(np.abs(angle_sequence) > self.min_angle)[0] + 1
    # Select the index of the points with the greatest theta                .
    # Large theta is associated with greatest change in direction.
    #sequence = list(filter(lambda angle: np.abs(angle) < self.min_angle, angle_sequence))
    sequence = []
    sequence.append(0)
    for angle in angle_sequence:
        if np.abs(angle) > 15:
            sequence.append(angle)
    sequence = list(np.diff(sequence))
    sequence.append(0)
    #print(sequence)

    return sequence

def visualize_path(trajectory, simplified, corners):
    trajectory = np.array(trajectory)
    sx, sy = simplified.T
    x, y = trajectory.T

    # Visualize trajectory and its simplified version.
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y, 'r--', label='trajectory')
    ax.plot(sx, sy, 'b-', label='simplified trajectory')
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.legend(loc='best')

    # Select the index of the points with the greatest theta.
    # Large theta is associated with greatest change in direction.
    idx = np.where(np.abs(corners) > 15)[0]
    print(idx)
    print(corners)

    try:

        # Visualize valuable turning points on the simplified trjectory.
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(sx, sy, 'gx-', label='simplified trajectory')
        ax.plot(sx[idx], sy[idx], 'ro', markersize=7, label='turning points')
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.legend(loc='best')
        plt.show()
    except:
        print('exception')

if __name__ == '__main__':
    # Build simplified (approximated) trajectory
    # using RDP algorithm.
    trajectory = [[5.9375, 1.525], [5.9125, 1.525], [5.8875, 1.525], [5.8625, 1.525], [5.8375, 1.525], [5.8125, 1.525], [5.7875, 1.525], [5.7625, 1.525], [5.7375, 1.525], [5.7125, 1.525], [5.6875, 1.5], [5.6625, 1.5], [5.6375, 1.5], [5.6125, 1.5], [5.6125, 1.475], [5.5875, 1.475], [5.5625, 1.475], [5.5375, 1.475], [5.4875, 1.475], [5.4875, 1.45], [5.4625, 1.45], [5.4375, 1.45], [5.4125, 1.45], [5.3875, 1.45], [5.3375, 1.45], [5.3125, 1.425], [5.2875, 1.425], [5.2625, 1.425], [5.2125, 1.425], [5.2125, 1.375], [5.1875, 1.375], [5.1625, 1.375], [5.1125, 1.375], [5.0875, 1.35], [5.0375, 1.35], [5.0125, 1.35], [4.9625, 1.35], [4.9375, 1.3], [4.8875, 1.3], [4.8125, 1.3], [4.7375, 1.275], [4.6625, 1.275], [4.6125, 1.225], [4.5875, 1.225], [4.4625, 1.225], [4.4125, 1.2], [4.3875, 1.2], [4.3375, 1.2], [4.2875, 1.2], [4.2625, 1.15], [4.2125, 1.15], [4.1375, 1.15], [4.1375, 1.1], [4.0375, 1.1], [3.9875, 1.1], [3.9375, 1.1], [3.8875, 1.075], [3.8125, 1.075], [3.7625, 1.025], [3.6625, 1.025], [3.6125, 1.025], [3.5125, 0.975], [3.4625, 0.975], [3.4375, 0.975], [3.3375, 0.925], [3.2875, 0.925], [3.2375, 0.925], [3.1375, 0.875], [3.0375, 0.875], [2.9375, 0.825], [2.8375, 0.825], [2.7875, 0.775], [2.7375, 0.775], [2.6875, 0.775], [2.5375, 0.725], [2.4875, 0.725], [2.4375, 0.725], [2.3875, 0.675], [2.3375, 0.675], [2.2875, 0.675], [2.2375, 0.625], [2.1875, 0.625], [2.0875, 0.625], [2.0375, 0.575], [1.9875, 0.575], [1.9375, 0.575], [1.8875, 0.575], [1.8625, 0.575], [1.8625, 0.525], [1.7375, 0.525], [1.7125, 0.5], [1.6625, 0.5], [1.6375, 0.5], [1.5875, 0.5], [1.5625, 0.45], [1.5125, 0.45], [1.4875, 0.425], [1.4375, 0.425], [1.4125, 0.425], [1.3875, 0.425], [1.3375, 0.425], [1.3125, 0.4], [1.2875, 0.4], [1.2625, 0.4], [1.2625, 0.35], [1.2375, 0.35], [1.2125, 0.35], [1.1875, 0.35], [1.1625, 0.35], [1.1375, 0.35], [1.1375, 0.325], [1.1125, 0.325], [1.0875, 0.325], [1.1125, 0.325], [1.1125, 0.325], [1.1375, 0.325], [1.1625, 0.325], [1.1875, 0.325], [1.1875, 0.35], [1.2125, 0.35], [1.2375, 0.35], [1.2375, 0.375], [1.2625, 0.375], [1.2875, 0.375], [1.3125, 0.375], [1.3375, 0.375], [1.3625, 0.4], [1.3875, 0.4], [1.4125, 0.4], [1.4375, 0.425], [1.4625, 0.425], [1.5125, 0.425], [1.5375, 0.425], [1.5625, 0.475], [1.5875, 0.475], [1.6125, 0.475], [1.6625, 0.5], [1.6875, 0.5], [1.7125, 0.5], [1.7375, 0.5], [1.8125, 0.525], [1.8375, 0.525], [1.8625, 0.525], [1.8875, 0.55], [1.9125, 0.55], [1.9625, 0.55], [1.9875, 0.55], [2.0125, 0.55], [2.0375, 0.575], [2.0875, 0.575], [2.1375, 0.575], [2.1875, 0.625], [2.2375, 0.625], [2.3875, 0.65], [2.4375, 0.65], [2.4625, 0.65], [2.5625, 0.7], [2.6125, 0.7], [2.6375, 0.7], [2.7375, 0.7], [2.7625, 0.75], [2.9125, 0.75], [2.9375, 0.775], [2.9875, 0.775], [3.0375, 0.775], [3.1875, 0.825], [3.2375, 0.825], [3.2875, 0.825], [3.3625, 0.875], [3.4125, 0.875], [3.4625, 0.875], [3.5125, 0.875], [3.6125, 0.925], [3.6625, 0.925], [3.7625, 0.975], [3.8125, 0.975], [3.8625, 0.975], [3.9625, 1.025], [4.0125, 1.025], [4.1125, 1.025], [4.1625, 1.075], [4.2625, 1.075], [4.3125, 1.125], [4.4125, 1.125], [4.5125, 1.175], [4.5625, 1.175], [4.6125, 1.225], [4.7125, 1.225], [4.8125, 1.225], [4.8625, 1.275], [4.9625, 1.275], [5.1625, 1.325], [5.2125, 1.375], [5.3125, 1.375], [5.3625, 1.425], [5.4625, 1.425], [5.5625, 1.425], [5.6125, 1.475], [5.7125, 1.475], [5.7625, 1.525], [5.8625, 1.525], [5.9625, 1.575], [6.0125, 1.575], [6.1125, 1.625], [6.1625, 1.625], [6.2125, 1.675], [6.3125, 1.675], [6.3625, 1.675], [6.4125, 1.725], [6.5125, 1.725], [6.6125, 1.775], [6.6625, 1.775], [6.7125, 1.775], [6.8125, 1.825], [6.8625, 1.825], [6.9125, 1.825], [6.9625, 1.875], [7.0125, 1.875], [7.0625, 1.875], [7.1125, 1.925], [7.1625, 1.925], [7.2625, 1.925], [7.3125, 1.975], [7.4125, 1.975], [7.4625, 1.975], [7.5125, 2.025], [7.5375, 2.025], [7.5875, 2.025], [7.6375, 2.075], [7.6875, 2.075], [7.7375, 2.075], [7.7625, 2.075], [7.8125, 2.125], [7.8625, 2.125], [7.8875, 2.125], [7.8875, 2.15], [7.9375, 2.15], [7.9875, 2.15], [8.5125, 1.95], [8.5375, 1.95], [8.5375, 1.925], [8.5875, 1.925], [8.6125, 1.9], [8.6375, 1.875], [8.6625, 1.875], [8.6625, 1.85], [8.6875, 1.85], [8.6875, 1.825], [8.7125, 1.825], [8.7125, 1.8], [8.7375, 1.8], [8.7125, 1.8], [8.6875, 1.8], [8.6875, 1.775], [8.6625, 1.775], [8.6375, 1.775], [8.6375, 1.75], [8.6125, 1.75], [8.5875, 1.725], [8.5625, 1.725], [8.5375, 1.7], [8.5125, 1.675], [8.4875, 1.675], [8.4875, 1.65], [8.4625, 1.65], [8.4375, 1.625], [8.4125, 1.625], [8.3875, 1.6], [8.3625, 1.575], [8.3375, 1.575], [8.3375, 1.55], [8.3125, 1.55], [8.3125, 1.525], [8.2625, 1.525], [8.2375, 1.5], [8.2125, 1.5], [8.1875, 1.45], [8.1375, 1.425], [8.1125, 1.375], [8.0625, 1.375], [8.0625, 1.35], [8.0375, 1.35], [8.0375, 1.325], [8.0125, 1.275], [7.9625, 1.275], [7.9375, 1.25], [7.8875, 1.175], [7.8625, 1.175], [7.8375, 1.15], [7.7875, 1.1], [7.7875, 1.075], [7.7625, 1.075], [7.7625, 1.025], [7.7625, 1.0], [7.7125, 1.0], [7.6875, 1.0], [7.6875, 0.975], [7.6625, 0.925], [7.6625, 0.9], [7.6375, 0.9], [7.6375, 0.875], [7.5875, 0.875], [7.5875, 0.85], [7.5625, 0.85], [7.5625, 0.825], [7.5375, 0.8], [7.5375, 0.775], [7.5125, 0.775], [7.5125, 0.75], [7.4875, 0.75], [7.4875, 0.725], [7.4875, 0.7], [7.4625, 0.7], [7.4625, 0.675], [7.4375, 0.675], [7.4375, 0.65], [7.4375, 0.625], [7.4125, 0.625], [7.4125, 0.6], [7.3875, 0.575], [7.3875, 0.55], [7.3875, 0.525], [7.3875, 0.5], [7.3875, 0.475], [7.3875, 0.45], [7.3875, 0.425], [7.3625, 0.425], [7.3625, 0.4], [7.3625, 0.375], [7.3375, 0.375], [7.3375, 0.375]]
    get_corner_angle_sequence_from_position(trajectory)

    '''
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
    '''


