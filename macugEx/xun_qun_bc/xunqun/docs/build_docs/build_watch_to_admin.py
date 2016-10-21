# -*- coding: utf-8 -*-
import subprocess

if __name__ == '__main__':
    status = subprocess.call(['mkdocs', 'build', '--clean', '-f', 'mkdocs_watch.yml'])
    subprocess.call(['rm -rf ../../admin/static/docs/watch/*'], shell=True)
    subprocess.call(['mv -f ./site/css ./site/img ./site/fonts ./site/js ./site/mkdocs ../../admin/static/docs/watch/'],
                    shell=True)
    subprocess.call(['rm -rf ../../admin/templates/docs/watch/*'], shell=True)
    subprocess.call(['mv -f ./site/* ../../admin/templates/docs/watch/'], shell=True)
    subprocess.call(['rm -rf ./site'], shell=True)
