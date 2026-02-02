from setuptools import find_packages, setup

package_name = 'fetchbot_language'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='rasika-lokhande',
    maintainer_email='rasika246@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fetch_cmd_parser=fetchbot_language.fetch_cmd_parser:main',
            'fetch_cmd_parser_client=fetchbot_language.fetch_cmd_parser_client:main'
        ],
    },
)
