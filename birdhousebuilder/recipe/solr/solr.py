# -*- coding: utf-8 -*-

"""Recipe solr"""

import os
from mako.template import Template

from birdhousebuilder.recipe import conda, supervisor

templ_solrconfig = Template(filename=os.path.join(os.path.dirname(__file__), "solrconfig.xml"))

class Recipe(object):
    """This recipe is used by zc.buildout"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        b_options = buildout['buildout']
        
        self.prefix = self.options.get('prefix', conda.prefix())
        self.options['prefix'] = self.prefix
        
        self.options['hostname'] = options.get('hostname', 'localhost')
        self.options['http_port'] = options.get('http_port', '8091')
        self.options['sites'] = options.get('sites', 'birdhouse')
        self.options['user'] = options.get('user', '')


    def install(self):
        installed = []
        installed += list(self.install_solr())
        #installed += list(self.install_config())
        installed += list(self.install_supervisor())
        return tuple()

    def install_solr(self, update=False):
        script = conda.Recipe(
            self.buildout,
            self.name,
            {'pkgs': 'solr'})
        
        if update == True:
            return script.update()
        else:
            return script.install()
        
    def install_config(self):
        """
        install solr config in ...
        """
        result = templ_solrconfig.render(**self.options)
        output = os.path.join(self.prefix, 'etc', 'solr', 'solrconfig.xml')
        conda.makedirs(os.path.dirname(output))
                
        try:
            os.remove(output)
        except OSError:
            pass

        with open(output, 'wt') as fp:
            fp.write(result)
        return [output]

    def install_supervisor(self, update=False):
        solr_dir = os.path.join(self.prefix, 'opt', 'solr')
        script = supervisor.Recipe(
            self.buildout,
            self.options.get('sites'),
            {'user': self.options.get('user'),
             'program': 'solr',
             'command': '{0}/bin/solr start -f -p {1}'.format(solr_dir, self.options.get('port')),
             'directory': solr_dir,
             'stopwaitsecs': '30',
             'killasgroup': 'true',
             })
        if update == True:
            return script.update()
        else:
            return script.install()

    def update(self):
        self.install_solr(update=True)
        #self.install_config()
        self.install_supervisor(update=True)
        return tuple()

def uninstall(name, options):
    pass

