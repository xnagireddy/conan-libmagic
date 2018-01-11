#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, AutoToolsBuildEnvironment, tools
import os


class LibmagicConan(ConanFile):
    name = "libmagic"
    version = "5.29"
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
        source_url = "https://github.com/file/file"
        filename_root = "FILE{0}".format(self.version.replace('.', '_'))
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, filename_root))
        extracted_dir = "file-{0}".format(filename_root)
        os.rename(extracted_dir, self.source_subfolder)
        #Rename to "sources" is a convention to simplify later steps

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("cygwin_installer/2.9.0@bincrafters/stable")
            if self.settings.compiler != "Visual Studio":
                self.build_requires("mingw_installer/1.0@conan/stable")

    def configure(self):
        del self.settings.compiler.libcxx

    def _build_visual_studio(self):
        raise Exception("not implemented")

    def _build_mingw(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        unix_environment = {}
        for key, value in env_build.vars.items():
            unix_environment[key] = value.replace("\\", "/")
        with tools.environment_append(unix_environment):
            configure_args = ['--prefix="%s"' % self.package_folder]
            configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
            configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
            if self.settings.arch == "x86_64":
                configure_args.append('--host=x86_64-w64-mingw32')
            if self.settings.arch == "x86":
                configure_args.append('--build=i686-w64-mingw32')
                configure_args.append('--host=i686-w64-mingw32')
            with tools.chdir(self.source_subfolder):
                tools.run_in_windows_bash(self, tools.unix_path("autoreconf -f -i"))
                tools.run_in_windows_bash(self, tools.unix_path("./configure %s" % ' '.join(configure_args)))
                tools.run_in_windows_bash(self, tools.unix_path("make"))
                tools.run_in_windows_bash(self, tools.unix_path("make install"))

    def _build_autotools(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = True
        if self.settings.arch == "x86":
            env_build.flags.append('-m32')
        elif self.settings.arch == "x86_64":
            env_build.flags.append('-m64')
        with tools.environment_append(env_build.vars):
            configure_args = ['--prefix=%s' % self.package_folder]
            configure_args.append('--enable-shared' if self.options.shared else '--disable-shared')
            configure_args.append('--enable-static' if not self.options.shared else '--disable-static')
            with tools.chdir(self.source_subfolder):
                self.run("autoreconf -f -i")
                env_build.configure(args=configure_args)
                env_build.make(args=["all"])
                env_build.make(args=["install"])


    def build(self):
        if self.settings.os == "Windows" and self.settings.compiler == "gcc":
            self._build_mingw()
        elif self.settings.os == "Windows" and self.settings.compiler == "Visual Studio":
            self._build_visual_studio()
        else:
            self._build_autotools()
        

    def package(self):
        with tools.chdir("sources"):
            self.copy(pattern="COPYING")
            # self.copy(pattern="magic.h", dst="include", src="src")
            # self.copy(pattern="*.dll", dst="bin", src="bin", keep_path=False)
            # self.copy(pattern="*.lib", dst="lib", src="lib", keep_path=False)
            # self.copy(pattern="*.a", dst="lib", src="lib", keep_path=False)
            # self.copy(pattern="*.so*", dst="lib", src="lib", keep_path=False)
            # self.copy(pattern="*.dylib", dst="lib", src="lib", keep_path=False)
            # self.copy("magic.mgc", dst="share/misc", src="magic", keep_path=False)
            # self.copy(pattern="*", dst="share/misc/magic", src="magic/Magdir", keep_path=False)


    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
