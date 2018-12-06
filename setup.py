from setuptools import setup, find_packages

setup(
    name='OpenWifi-Web',
    version="0.1",
    description="Webviews for OpenWifi",
    author="Johannes Wegener",
    install_requires=["OpenWifi"],
    entry_points="""
    [OpenWifi.plugin]
    addPluginRoutes=OpenWifiWeb:addPluginRoutes
    globalPluginViews=OpenWifiWeb:globalWebViews
    """,
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '' : ["static/*", "static/*/*", "static/*/*/*", "templates/*", "upload/.gitkeep"]
        }
)
