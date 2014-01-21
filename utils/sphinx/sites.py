import os.path
import re

from utils.project import mms_should_migrate
from utils.jobs.dependency import check_dependency
from utils.files import expand_tree, create_link, copy_if_needed

def manual_single_html(input_file, output_file):
    # don't rebuild this if its not needed.
    if check_dependency(output_file, input_file) is True:
        pass
    else:
        print('[process] [single]: singlehtml not changed, not reprocessing.')
        return False

    with open(input_file, 'r') as f:
        text = f.read()

    text = re.sub('href="contents.html', 'href="index.html', text)
    text = re.sub('name="robots" content="index"', 'name="robots" content="noindex"', text)
    text = re.sub('(href=")genindex.html', '\1../genindex/', text)

    with open(output_file, 'w') as f:
        f.write(text)

    print('[process] [single]: processed singlehtml file.')

#################### Sphinx Post-Processing ####################

def finalize_epub_build(conf):
    epub_name = '-'.join(conf.project.title.lower().split())
    epub_branched_filename = epub_name + '-' + conf.git.branches.current + '.epub'
    epub_src_filename = epub_name + '.epub'

    if conf.project.name == 'mms' and mms_should_migrate(builder, conf) is False:
        return False

    copy_if_needed(source_file=os.path.join(conf.paths.projectroot,
                                            conf.paths.branch_output,
                                            'epub', epub_src_filename),
                   target_file=os.path.join(conf.paths.projectroot,
                                            conf.paths.public_site_output,
                                            epub_branched_filename))
    create_link(input_fn=epub_branched_filename,
                 output_fn=os.path.join(conf.paths.projectroot,
                                        conf.paths.public_site_output,
                                        epub_src_filename))


def get_single_html_dir(conf):
    return os.path.join(conf.paths.public_site_output, 'single')

def finalize_single_html_jobs(builder, conf):
    if conf.project.name == 'mms' and mms.should_migrate(builder, conf) is False:
        raise StopIteration

    pjoin = os.path.join

    single_html_dir = get_single_html_dir(conf)

    if not os.path.exists(single_html_dir):
        os.makedirs(single_html_dir)

    try:
        manual_single_html(input_file=pjoin(conf.paths.branch_output,
                                                    builder, 'contents.html'),
                                   output_file=pjoin(single_html_dir, 'index.html'))
    except (IOError, OSError):
        manual_single_html(input_file=pjoin(conf.paths.branch_output,
                                                    builder, 'index.html'),
                                   output_file=pjoin(single_html_dir, 'index.html'))
    copy_if_needed(source_file=pjoin(conf.paths.branch_output,
                                     builder, 'objects.inv'),
                   target_file=pjoin(single_html_dir, 'objects.inv'))

    single_path = pjoin(single_html_dir, '_static')

    for fn in expand_tree(pjoin(conf.paths.branch_output,
                                builder, '_static'), None):

        yield {
            'job': copy_if_needed,
            'args': [fn, pjoin(single_path, os.path.basename(fn))],
            'target': None,
            'dependency': None
        }

def finalize_dirhtml_build(builder, conf):
    pjoin = os.path.join

    process.error_pages(conf)

    single_html_dir = get_single_html_dir(conf)
    search_page = pjoin(conf.paths.branch_output, builder, 'index.html')

    if conf.project.name == 'mms' and mms.should_migrate(builder, conf) is False:
        return False

    if os.path.exists(search_page):
        copy_if_needed(source_file=search_page,
                       target_file=pjoin(single_html_dir, 'search.html'))

    dest = pjoin(conf.paths.projectroot, conf.paths.public_site_output)
    command('rsync -a {source}/ {destination}'.format(source=pjoin(conf.paths.projectroot,
                                                                 conf.paths.branch_output,
                                                                 builder),
                                                    destination=dest))

    print('[{0}]: migrated build to {1}'.format(builder, dest))

    if conf.git.branches.current in conf.git.branches.published:
        sitemap_exists = generate.sitemap(config_path=None, conf=conf)

        if sitemap_exists is True:
            copy_if_needed(source_file=pjoin(conf.paths.projectroot,
                                             conf.paths.branch_output,
                                             'sitemap.xml.gz'),
                           target_file=pjoin(conf.paths.projectroot,
                                             conf.paths.public_site_output,
                                             'sitemap.xml.gz'))

    sconf = BuildConfiguration('sphinx.yaml', pjoin(conf.paths.projectroot,
                                                conf.paths.builddata))

    if 'dirhtml' in sconf and 'excluded_files' in sconf.dirhtml:
        fns = [ pjoin(conf.paths.projectroot,
                      conf.paths.public_site_output,
                      fn)
                for fn in sconf.dirhtml.excluded_files ]

        cleaner(fns)
        print('[dirhtml] [clean]: removed excluded files from output directory')
