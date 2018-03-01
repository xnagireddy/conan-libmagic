#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, VisualStudioBuildEnvironment, AutoToolsBuildEnvironment, tools
import os


class LibmagicConan(ConanFile):
    name = "libmagic"
    version = "5.25"
    url = "https://github.com/bincrafters/conan-libmagic"
    description = "This library can be used to classify files according to magic number tests."
    license = "https://github.com/file/file/blob/master/COPYING"
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=False"
    #use static org/channel for libs in conan-center
    #use version ranges for dependencies unless there's a reason not to
    requires = "zlib/[>=1.2.8]@conan/stable"

    source_subfolder = "sources"
        
    # def requirements(self):
    #     #use dynamic org/channel for libs in bincrafters
    #     self.requires.add("libuv/[>=1.15.0]@bincrafters/stable")

    def source(self):
        source_url = ":q"
        filename_root = "FILE{0}".format(self.version.replace('.', '_'))
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, filename_root))
        extracted_dir = "file-{0}".format(filename_root)
        os.rename(extracted_dir, self.source_subfolder)
        #Rename to "sources" is a convention to simplify later steps

    def _build_autotools(self):
        with tools.chdir("sources"):

            env_build = AutoToolsBuildEnvironment(self)
            env_build.fpic = True

            with tools.environment_append(env_build.vars):
                config_args = ['--prefix=%s' % self.package_folder]
                for option_name in self.options.values.fields:
                    if(option_name == "shared"):
                        if(getattr(self.options, "shared")):
                            config_args.append("--enable-shared")
                            config_args.append("--disable-static")
                        else:
                            config_args.append("--enable-static")
                            config_args.append("--disable-shared")
                    else:
                        activated = getattr(self.options, option_name)
                        if activated:
                            self.output.info("Activated option! %s" % option_name)
                            config_args.append("--%s" % option_name)

                self.run("autoreconf -f -i")
                env_build.configure(args=config_args)
                env_build.make()

    def build(self):
        if self.settings.compiler == 'Visual Studio':
            # self.build_vs()
            self.output.fatal("No windows support yet. Sorry. Help a fellow out and contribute back?")

        # path_env = os.environ['PATH']
        # path = os.path.join(self.build_folder, os.path.join(self.source_subfolder, "src"))
        # path_env = "{0}:{1}".format(path, path_env)

        # with tools.environment_append({'PATH': path_env}):
            # self._build_autotools()
        self._build_autotools()

    def package(self):
        with tools.chdir(self.source_subfolder):
            self.copy(pattern="COPYING")
            self.copy(pattern="magic.h", dst="include", src="src")
            self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)
            self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)
            self.copy("magic.mgc", dst="share/misc", src="magic", keep_path=False)
            self.copy(pattern="*", dst="share/misc/magic", src="magic/Magdir", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
