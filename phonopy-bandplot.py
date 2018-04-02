 #!/Users/raymond/anaconda2/bin/python

import sys
import numpy as np

try:
    import yaml
except ImportError:
    print("You need to install python-yaml.")
    sys.exit(1)

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def dot_product(local_modes, normal_modes):
	sum = 0.0
	for i, mode in enumerate(local_modes):
		for j, xyz in enumerate(mode):
			sum += np.dot(xyz, normal_modes[i][j])
	return sum


def reordering(freq_vec, local_modes, normal_modes):
    outvec = []
    for j, nmod in enumerate(normal_modes):
        max_overlap = 0.0
        second_largest = 0.0
        max_index = 0
        for k, lmod in enumerate(local_modes):
            overlap = dot_product(local_modes[k], normal_modes[j])
            if overlap > max_overlap:
                second_largest = max_overlap
                max_overlap = overlap
                max_index = k
        outvec.append(freq_vec[max_index])
    return outvec


def read_band_yaml(filename):
    data = yaml.load(open(filename), Loader=Loader)
    raw_frequencies = []
    ordered_frequencies = []
    distances = []
    global_eigenvecs = []
    for j, v in enumerate(data['phonon']):
        raw_frequencies.append([f['frequency'] for f in v['band']])
        distances.append(v['distance'])
        global_eigenvecs.append([eigvecs['eigenvector'] for eigvecs in v['band']])

    normal_modes = global_eigenvecs[0]
    for i, local_freq in enumerate(raw_frequencies):
        if i == 0:
            continue
        local_modes = global_eigenvecs[i]
        ordered_frequencies.append(reordering(local_freq, local_modes, normal_modes))
        normal_modes = local_modes

    return (np.array(distances),
            np.array(ordered_frequencies),
            data['segment_nqpoint'])


def main():
    filename = 'band.yaml'

    (distances, frequencies, segment_nqpoint) = read_band_yaml(filename)
 
    end_points = [0,]
    for nq in segment_nqpoint:
        end_points.append(nq + end_points[-1])
    end_points[-1] -= 1
    segment_positions = distances[end_points]

    for j, freqs in enumerate(frequencies.T):
        q = 0
        for nq in segment_nqpoint:
            for d, f in zip(distances[q:(q + nq)],
                            freqs[q:(q + nq)]):
                print("%f %f" % (d, f))
            q += nq
            print('')
        print('')


if __name__ == "__main__":
    main()
