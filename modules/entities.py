import glob
import os
from enum import Enum, auto

from bbox.AndroidManifest import AndroidManifest
from modules import config, shell
from modules.exceptions import ManifestNotFoundException

class Type(Enum):
    ORIGINAL = auto()
    INSTRUMENTED = auto()

class Apk:
    def __init__(self, name, type):
        if type == Type.ORIGINAL:
            self.path = os.path.join(config.APK_REPOSITORY, name)
        elif type == Type.INSTRUMENTED:
            self.path = os.path.join(config.TEST_REPOSITORY, name)
        self.name = name
        self.package = shell.get_package(self.path)
        self.manifest = None
        self.type = type

    def init_manifest(self):
        sources_path = os.path.join(config.SOURCES_REPOSITORY, self.name.split('.apk')[0])
        manifest_path = self.get_android_manifest_path(sources_path)
        self.manifest = AndroidManifest(manifest_path)

    def get_android_manifest_path(self, sources_path):
        android_manifest_path = os.path.join(sources_path, "app", "src", "main", "AndroidManifest.xml")
        if not os.path.exists(android_manifest_path):
            android_manifest_path = os.path.join(sources_path, "src", "main", "AndroidManifest.xml")
            if not os.path.exists(android_manifest_path):
                try:
                    android_manifest_path = self.search_for_manifest(sources_path)
                except StopIteration:
                    raise ManifestNotFoundException()
                if not os.path.exists(android_manifest_path):
                    raise Exception("Manifest not found")
        return android_manifest_path

    def search_for_manifest(self, sources_path):
        generator = glob.iglob(f'{sources_path}/**/AndroidManifest.xml', recursive=True)
        android_manifest_path = next(generator)
        return android_manifest_path
