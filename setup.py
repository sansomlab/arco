from setuptools import setup

setup(name='arco',
            version='0.1',
            description='Automatic Report Compiler',
            url='http://github.com/sansomlab/arco',
            author='Steve Sansom',
            author_email='stephen.sansom@kennedy.ox.ac.uk',
            license='Apache 2.0',
            packages=['arco'],
            entry_points = {
                'console_scripts': ['arco=arco.arco:main'],
                },
            zip_safe=False)
