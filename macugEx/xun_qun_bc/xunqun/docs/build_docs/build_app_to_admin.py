# -*- coding: utf-8 -*-
import subprocess
from jinja2 import Template


def main():
    import sys
    sys.path.append('../..')
    import setting

    template = Template(open('../docs_app/push.tpl', 'r').read().decode('utf-8-sig'))
    md = template.render(username=setting.mqtt['cli_username'], password=setting.mqtt['cli_password'],
                         prefix=setting.mqtt['prefix'])
    with open('../docs_app/push.md', 'w') as push_md:
        push_md.write(md.encode('utf-8'))

    status = subprocess.call(['mkdocs', 'build', '--clean', '-f', 'mkdocs_app.yml'])

    subprocess.call(['rm -rf ../../admin/static/docs/app/*'], shell=True)
    subprocess.call(['mv -f ./site/css ./site/img ./site/fonts ./site/js ./site/mkdocs ../../admin/static/docs/app/'],
                    shell=True)
    subprocess.call(['rm -rf ../../admin/templates/docs/app/*'], shell=True)
    subprocess.call(['mv -f ./site/* ../../admin/templates/docs/app/'], shell=True)
    subprocess.call(['rm -rf ./site'], shell=True)


if __name__ == '__main__':
    main()
