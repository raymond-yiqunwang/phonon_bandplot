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


def compute_overlap(local_modes, normal_modes):
    real_part = 0.0
    imag_part = 0.0
    for i, lmode in enumerate(local_modes):
        nmode = normal_modes[i]
        for j, ldim in enumerate(lmode):
            ndim = nmode[j]
            real_part += ldim[0]*ndim[0] - ldim[1]*ndim[1]
            imag_part += ldim[1]*ndim[0] + ldim[0]*ndim[1]
    print ''
    print real_part
    print imag_part
    print ''
    overlap = np.sqrt(real_part*real_part + imag_part*imag_part)
    return overlap


def reordering(freq_vec, local_modes, normal_modes):
    outvec = []
    outmode = []
    for j, nmod in enumerate(normal_modes):
        max_index = -1
        max_overlap = -1.0
        for k, lmod in enumerate(local_modes):
            overlap = compute_overlap(lmod, nmod)
            print overlap
            if overlap > max_overlap:
                max_overlap = overlap
                max_index = k
        print ('max_index : %d') %max_index
        outvec.append(freq_vec[max_index])
        outmode.append(local_modes[max_index])
    return (outvec, outmode)


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
            ordered_frequencies.append(local_freq)
            continue
        local_modes = global_eigenvecs[i]
        print ('before reoredering')
        (new_frequencies, new_modes) = reordering(local_freq, local_modes, normal_modes)
        print ('after reoredering')
        ordered_frequencies.append(new_frequencies)
        normal_modes = new_modes

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
