from setuptools import setup, find_packages

setup(name='GeoNodePy',
      version= __import__('geonode').get_version(),
      description="Application for serving and sharing geospatial data",
      long_description=open('README.rst').read(),
      classifiers=[
        "Development Status :: 1 - Planning" ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='GeoNode Developers',
      author_email='dev@geonode.org',
      url='http://geonode.org',
      license='GPL',
      packages = find_packages(),
      include_package_data=True,
      install_requires = [
        'OWSLib==0.5.1',
        'Django==1.4',
        'httplib2==0.7.4',
        'gsconfig==0.6.0',
        'django-registration==0.8',
        'django-profiles==0.2',
        'geonode-avatar==2.1',
        'dialogos==0.1',
        'agon-ratings==0.2',
        'South==0.7.3',
        'django-taggit==0.9.3',
          ],
      zip_safe=False,
      entry_points="""
      # -*- Entry points: -*-
      """,
      )


