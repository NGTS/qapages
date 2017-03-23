from contextlib import contextmanager
import os
from collections import namedtuple
import shutil
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as Canvas
from matplotlib.figure import Figure
import pymysql
from pymysql.cursors import DictCursor
import warnings
import numpy as np
import json

__all__ = [
    'add_click_regions',
    'compute_night_boundaries',
    'copy_manifest_files',
    'create_empty',
    'figure_context',
    'find_existing_job_files',
    'find_file',
    'find_previous_job_files',
    'get_url',
    'mark_nights',
    'render_regionfile',
    'update_manifest',
]

# Disable the annoying warnings
warnings.simplefilter('ignore')

# Customise the figures
# plt.style.use('seaborn')
mpl.rc('figure', figsize=(6, 5), dpi=100)
mpl.rc('axes', grid=True)
mpl.rc('lines', markersize=3, markeredgewidth=0.0)
mpl.rc('text', usetex=False)
mpl.rc('font', family='sans-serif')


def add_click_regions(axis, night_boundaries, region_filename, prod_ids, manifest_path):
    ''' Mark regions on the figure, and render a region file to disk.
    '''
    # Only select some of the labels to print
    label_idx = np.linspace(
        0, len(night_boundaries[0]) - 1, 10).astype(np.int32)

    mark_nights(axis, night_boundaries)
    axis.set_xticks(night_boundaries[0][label_idx])
    axis.set_xticklabels(night_boundaries[1][label_idx], rotation=90)

    # Make sure to finish rendering the figure before rendering these regions,
    # including calling `tight_layout`
    render_regionfile(axis, region_filename, night_boundaries, prod_ids, manifest_path)


def compute_night_boundaries(nights):
    ''' Given an iterable of nights, compute the indices
    and unique values for the nights.

    Returns a tuple of (indices, labels)
    '''
    indices, labels = [], []
    indices.append(0)
    labels.append(nights[0])

    last_night = nights[0]
    for i, night in enumerate(nights):
        if night != last_night:
            indices.append(i)
            labels.append(night)
            last_night = night

    return np.array(indices), np.array(labels)


def copy_manifest_files(manifest_path, webserver_dir):
    with open(manifest_path) as infile:
        filenames = (line.strip() for line in infile
            if line.strip())
        for filename in filenames:
            if os.path.isfile(filename):
                destination = os.path.join(webserver_dir, filename)
                print('Copying {} to {}'.format(
                    filename, destination))
                shutil.copyfile(filename, destination)


def create_empty(filename):
    with open(filename, 'w') as outfile:
        pass


@contextmanager
def figure_context(filename, *args, **kwargs):
    ''' Create a saveable figure context, simplifying figure setup.

    Ensures `tight_layout` has been called on the figure, and
    automatically renders the plot to disk.
    '''
    fig = Figure(*args, **kwargs)
    canvas = Canvas(fig)
    yield fig
    fig.tight_layout()
    canvas.print_figure(filename)


def find_existing_job_files(prod_id):
    ''' Given the product id of a previous job - one that has already
    been run through the pipeline, and _must_ exist!!! - return the
    paths of the files in the prodstore.
    '''
    with connect_to_database() as cursor:
        cursor.execute(
            '''SELECT
                LOWER(sub_type) as filetype,
                CONCAT_WS('/',directory,filename) AS path
            FROM prod_dir
            JOIN prod_cat USING (prod_id)
            WHERE prod_id = %s''',
            (prod_id, )
            )
        results = cursor.fetchall()

    return {
        row['filetype']: row['path']
        for row in results
    }


def find_file(root, file_type):
    ''' Given a file root and measurement type, return the path (without
    directory) of the corresponding file.

    The code also checks that the file exists, and prints an error
    message if not.
    '''
    try:
        stub = {
            'imagelist': '_IMAGELIST.fits',
            'catalogue': '_CATALOGUE.fits',
            'sysrem_catalogue': '_SYSREM_CATALOGUE.fits',
            'sysrem_flux': '_SYSREM_FLUX3.fits',
        }[file_type.lower()]
    except KeyError:
        raise RuntimeError('Unsupported file type for find_file function: {}'.format(file_type))
    path = root + stub
    assert os.path.isfile(path), 'cannot find file specified: {0}'.format(path)
    return path


def find_previous_job_files(prod_id, job_type):
    ''' Given the product id of the current job, and the type of the
    current job, compute the location of the files from the preceding
    step.

    Jobs progress in the current way:

    RefCatPipe -> PhotPipe -> MergePipe -> SysremPipe -> BLSPipe
    '''

    # TODO: finish this function for the other job types, if required
    job_type = job_type.lower()
    if job_type != 'sysrem':
        raise NotImplementedError(
            'Only sysrem jobs are supported for now')

    with connect_to_database() as cursor:
        cursor.execute(
            '''SELECT raw_prod_id
            FROM sysrempipe_prod
            WHERE prod_id = %s''',
            (prod_id, )
            )
        rows = cursor.fetchall()

    if len(rows) == 1:
        return find_existing_job_files(rows[0]['raw_prod_id'])

    elif len(rows) == 0:
        raise ValueError(
            'No results returned for {job_type} job: {prod_id}'.format(
                job_type=job_type,
                prod_id=prod_id,
                )
            )

    elif len(rows) > 1:
        raise ValueError(
            'Ambiguous number of jobs for {job_type} job: {prod_id}'.format(
                job_type=job_type,
                prod_id=prod_id,
                )
            )


def get_url(job_type, prod_id):
    ''' Given a job type and product it, return the root url of the job
    QA result.
    '''
    endpoints = {
        'phot': 'photpipe.php',
    }

    return '/ngtsqa/{endpoint}?prod_id={prod_id}'.format(
        endpoint=endpoints[job_type.lower()],
        prod_id=prod_id)


def mark_nights(axis, nights):
    to_shade = True
    for left, right in zip(nights[0][:-1], nights[0][1:]):
        if to_shade:
            axis.axvspan(left, right, color='0.8')
        to_shade = not to_shade


def render_regionfile(axis, output_filename, boundaries, prod_ids, manifest_path):
    assert len(boundaries[0]) == len(prod_ids) == len(boundaries[1])

#     hrefs = np.array([
#         get_url('phot', prod_id) for prod_id in prod_ids
#     ]).tolist()

    region_coordinates = fetch_region_coordinates(axis, boundaries[0])
    assert len(prod_ids) == len(region_coordinates)

    out = []
    for prod_id, region in zip(prod_ids, region_coordinates):
        if region.xmax > (region.xmin + 1):
            val = region._asdict()
            val['href'] = get_url('phot', prod_id)
            out.append(val)

    with open(output_filename, 'w') as outfile:
        json.dump(out, outfile, indent=2, cls=NumpyJsonEncoder)

    update_manifest(output_filename, manifest_path)



    # trans = FigureTransform(figure)

    # dummy = np.ones(len(boundaries[0])) * 0.4
    # results = trans.transform_pixels(boundaries[0], dummy)

    # xs = np.array(results['x'][:-1])
    # widths = np.diff(results['x'])

    # ind = widths >= 1
    # xs, widths = [data[ind] for data in [xs, widths]]

    # ylims = figure.get_axes()[0].get_ylim()
    # yrange_pix = trans.transform_pixels([0, 0], ylims)['y']
    # ys = np.ones_like(xs) * yrange_pix[0]
    # heights = np.ones_like(xs) * (yrange_pix[1] - yrange_pix[0])


    # out = []
    # for i in range(len(hrefs)):
    #     out.append({
    #         'xmin': int(xs[i]),
    #         'xmax': int(xs[i] + widths[i]),
    #         'ymin': yrange_pix[1],
    #         'ymax': yrange_pix[0],
    #         'href': hrefs[i],
    #     })

    # with open(output_filename, 'w') as outfile:
    #     json.dump(out, outfile, indent=2)

    # update_manifest(output_filename, manifest_path)


def update_manifest(filename, manifest_path):
    ''' Update the manifest file with the file path.
    '''
    with open(manifest_path, 'a') as outfile:
        outfile.write('{}\n'.format(filename))


# Private (non-exported) functions

@contextmanager
def connect_to_database(db='ngts_pipe'):
    with pymysql.connect(host='ngtsdb', db=db, cursorclass=DictCursor) as cursor:
        yield cursor


def fetch_region_coordinates(axis, x_positions):
    fig = axis.get_figure()
    canvas = Canvas(fig)
    trans = AxisTransform(canvas, axis)

    # Append the rightmost axis limit to the positions to include
    # a click region for the final region
    x_positions = list(x_positions) + [axis.get_xlim()[1]]
    return list(trans.x_regions(sorted(x_positions)))


Region = namedtuple('Region', ['xmin', 'xmax', 'ymin', 'ymax'])


class AxisTransform(object):

    def __init__(self, canvas, axis):
        self.canvas = canvas
        self.axis = axis

    def transform(self, x, y):
        x = np.atleast_1d(x)
        y = np.atleast_1d(y)

        points = np.array([x, y]).T
        x, y = self.axis.transData.transform(points).T
        _, height = self.canvas.get_width_height()
        return {
            'x': x.tolist(),
            'y': (height - y).tolist(),
        }

    def transform_pixels(self, *args, **kwargs):
        results = self.transform(*args, **kwargs)
        x, y = results['x'], results['y']
        return {
            'x': np.round(x).astype(np.int32).tolist(),
            'y': np.round(y).astype(np.int32).tolist(),
        }

    def x_regions(self, xvals):
        ylims = self.axis.get_ylim()
        x_results = self.transform_pixels(xvals, np.ones_like(xvals))['x']
        y_range = self.transform_pixels([0., 0.], ylims)['y']

        ymin = min(y_range)
        ymax = max(y_range)

        x_width = np.diff(x_results)

        for x_val, width in zip(x_results[:-1], x_width):
            region = Region(
                xmin=x_val,
                xmax=x_val + width,
                ymin=ymin,
                ymax=ymax)
            yield region


class NumpyJsonEncoder(json.JSONEncoder):
    def default(self, val):
        if isinstance(val, np.integer):
            return int(val)
        elif isinstance(val, np.floating):
            return float(val)
        elif isinstance(val, np.ndarray):
            return val.tolist()
        else:
            return super(NumpyJsonEncoder, self).default(val)
