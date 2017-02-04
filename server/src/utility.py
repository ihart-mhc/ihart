"""
Utility methods for the iHart server.
"""

import sys

def resource_path(resource):
    """
    Utility method to get absolute path to a resource
     (sometimes the current directory, sometimes the temp directory).
    @param resource the path to the resource from the location of this script
    @return absolute path to the resource
    """
    base_path = getattr(sys, "_MEIPASS", ".")
    return "/".join([base_path, resource])