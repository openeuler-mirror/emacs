%global _hardened_build 1
%bcond_with bootstrap

Name:          emacs
Epoch:         1
Version:       26.1
Release:       11
Summary:       An extensible GNU text editor
License:       GPLv3+ and CC0-1.0
URL:           http://www.gnu.org/software/emacs
Source0:       https://ftp.gnu.org/gnu/%{name}/%{name}-%{version}.tar.xz
Source3:       site-start.el
Source4:       default.el
Source7:       emacs.service

Patch1:        emacs-system-crypto-policies.patch
Patch2:        emacs-xft-color-font-crash.patch

BuildRequires: gcc atk-devel cairo-devel freetype-devel fontconfig-devel dbus-devel giflib-devel
BuildRequires: glibc-devel zlib-devel gnutls-devel libselinux-devel GConf2-devel alsa-lib-devel
BuildRequires: libxml2-devel bzip2 cairo texinfo gzip desktop-file-utils libacl-devel libtiff-devel
BuildRequires: libpng-devel libjpeg-turbo-devel libjpeg-turbo ncurses-devel gpm-devel libX11-devel
BuildRequires: libXau-devel libXdmcp-devel libXrender-devel libXt-devel libXpm-devel gtk3-devel
BuildRequires: xorg-x11-proto-devel webkit2gtk3-devel librsvg2-devel

%if !%{with bootstrap}
#BuildRequires: libotf-devel ImageMagick-devel m17n-lib-devel liblockfile-devel

# For lucid
BuildRequires: Xaw3d-devel
%endif

%ifarch %{ix86}
BuildRequires: util-linux
%endif

Requires:      desktop-file-utils dejavu-sans-mono-fonts
Requires:      emacs-common = %{epoch}:%{version}-%{release}
Requires(preun):     %{_sbindir}/alternatives
Requires(posttrans): %{_sbindir}/alternatives

Provides:      emacs(bin) = %{epoch}:%{version}-%{release}

%define site_lisp %{_datadir}/emacs/site-lisp
%define site_start_d %{site_lisp}/site-start.d
%define bytecompargs -batch --no-init-file --no-site-file -f batch-byte-compile
%define pkgconfig %{_datadir}/pkgconfig
%define emacs_libexecdir %{_libexecdir}/emacs/%{version}/%{_host}

%description
Emacs is the extensible, customizable, self-documenting real-time display editor.
At its core is an interpreter for Emacs Lisp, a dialect of the Lisp programming language
with extensions to support text editing. And it is an entire ecosystem of functionality beyond text editing,
including a project planner, mail and news reader, debugger interface, calendar, and more.

%if !%{with bootstrap}
%package       lucid
Summary:       GNU Emacs text editor with LUCID toolkit X support
Requires:      emacs-common = %{epoch}:%{version}-%{release}
Requires(preun):     %{_sbindir}/alternatives
Requires(posttrans): %{_sbindir}/alternatives
Provides:      emacs(bin) = %{epoch}:%{version}-%{release}

%description  lucid
This package provides an emacs binary with support for X windows
using LUCID toolkit.
%endif

%package       nox
Summary:       GNU Emacs text editor without X support
Requires:      emacs-common = %{epoch}:%{version}-%{release}
Requires(preun):     %{_sbindir}/alternatives
Requires(posttrans): %{_sbindir}/alternatives
Provides:      emacs(bin) = %{epoch}:%{version}-%{release}

%description   nox
This package provides an emacs binary with no X windows support for running
on a terminal

%package       common
Summary:       Emacs common files
License:       GPLv3+ and GFDL and BSD
Requires:      %{name}-filesystem = %{epoch}:%{version}-%{release}
Requires(preun):     /sbin/install-info
Requires(preun):     %{_sbindir}/alternatives
Requires(posttrans): %{_sbindir}/alternatives
Requires(post):      /sbin/install-info
Provides:      %{name}-el = %{epoch}:%{version}-%{release}
Obsoletes:     emacs-el < 1:24.3-29

%description   common
This package contains all the common files needed by emacs, emacs-lucid
or emacs-nox.

%package       filesystem
Summary:       Emacs filesystem layout
BuildArch:     noarch

%description   filesystem
Emacs filesystem layout

%package_help

%prep
%autosetup -n %{name}-%{version} -p1

autoconf

egrep -v "tetris.elc|pong.elc" lisp/Makefile.in > lisp/Makefile.in.new && mv lisp/Makefile.in.new lisp/Makefile.in

rm -f lisp/play/tetris.el* lisp/play/pong.el*

%define info_files ada-mode auth autotype bovine calc ccmode cl dbus dired-x ebrowse ede ediff edt efaq-w32 efaq eieio eintr elisp emacs-gnutls emacs-mime emacs epa erc ert eshell eudc eww flymake forms gnus htmlfontify idlwave ido info mairix-el message mh-e newsticker nxml-mode octave-mode org pcl-cvs pgg rcirc reftex remember sasl sc semantic ses sieve smtpmail speedbar srecode todo-mode tramp url vhdl-mode vip viper widget wisent woman

cd info
fs=( $(ls *.info) )
is=( %info_files  )
files=$(echo ${fs[*]} | sed 's/\.info//'g | sort | tr -d '\n')
for i in $(seq 0 $(( ${#fs[*]} - 1 ))); do
  if test "${fs[$i]}" != "${is[$i]}.info"; then
    echo Please update %%info_files: ${fs[$i]} != ${is[$i]}.info >&2
    break
  fi
done
cd ..

%ifarch %{ix86}
%define setarch setarch %{_arch} -R
%else
%define setarch %{nil}
%endif

ln -s ../../%{name}/%{version}/etc/COPYING doc
ln -s ../../%{name}/%{version}/etc/NEWS doc

%build
export CFLAGS="-DMAIL_USE_LOCKF %{optflags}"
export HARDENING_PIE=0

%if !%{with bootstrap}
# Build GTK+ binary
mkdir build-gtk && cd build-gtk
ln -s ../configure .

LDFLAGS=-Wl,-z,relro;  export LDFLAGS;

%configure --with-dbus --with-gif --with-jpeg --with-png --with-rsvg \
           --with-tiff --with-xft --with-xpm --with-x-toolkit=gtk3 --with-gpm=no \
           --with-xwidgets --with-modules   --without-libotf --without-m17n-flt --without-imagemagick
make bootstrap
%{setarch} %make_build
cd ..

# Build Lucid binary
mkdir build-lucid && cd build-lucid
ln -s ../configure .

LDFLAGS=-Wl,-z,relro;  export LDFLAGS;

%configure --with-dbus --with-gif --with-jpeg --with-png --with-rsvg \
           --with-tiff --with-xft --with-xpm --with-x-toolkit=lucid --with-gpm=no \
           --with-modules --without-libotf --without-m17n-flt --without-imagemagick
make bootstrap
%{setarch} %make_build
cd ..
%endif

# Build binary without X support
mkdir build-nox && cd build-nox
ln -s ../configure .
%configure --with-x=no --with-modules
%{setarch} %make_build
cd ..
rm build-{gtk,lucid,nox}/src/emacs-%{version}.*

# Generate pkgconfig file
cat > emacs.pc << EOF
sitepkglispdir=%{_datadir}/emacs/site-lisp
sitestartdir=%{site_lisp}/site-start.d

Name: emacs
Description: GNU Emacs text editor
Version: %{epoch}:%{version}
EOF

# Generate macros.emacs RPM macro file
cat > macros.emacs << EOF
%%_emacs_version %{version}
%%_emacs_ev %{?epoch:%{epoch}:}%{version}
%%_emacs_evr %{?epoch:%{epoch}:}%{version}-%{release}
%%_emacs_sitelispdir %{_datadir}/emacs/site-lisp
%%_emacs_sitestartdir %{site_lisp}/site-start.d
%%_emacs_bytecompile /usr/bin/emacs -batch --no-init-file --no-site-file --eval '(progn (setq load-path (cons "." load-path)))' -f batch-byte-compile
EOF

%install
cd build-gtk
%make_install
cd ..

rm %{buildroot}%{_bindir}/emacs
touch %{buildroot}%{_bindir}/emacs

gunzip %{buildroot}%{_datadir}/emacs/%{version}/lisp/jka*.el.gz

%if !%{with bootstrap}
install -p -m 0755 build-lucid/src/emacs %{buildroot}%{_bindir}/emacs-%{version}-lucid
%endif

install -p -m 0755 build-nox/src/emacs %{buildroot}%{_bindir}/emacs-%{version}-nox

chmod 755 %{buildroot}%{emacs_libexecdir}/movemail

# Confirm movemail don't setgid
mkdir -p %{buildroot}%{site_lisp}
install -p -m 0644 %SOURCE3 %{buildroot}%{_datadir}/emacs/site-lisp/site-start.el
install -p -m 0644 %SOURCE4 %{buildroot}%{_datadir}/emacs/site-lisp

echo "(setq source-directory \"%{_datadir}/emacs/%{version}/\")" >> %{buildroot}%{_datadir}/emacs/site-lisp/site-start.el

pushd %{buildroot}%{_bindir}
mv etags etags.emacs
mv ctags gctags
popd

pushd %{buildroot}%{_mandir}/man1
mv ctags.1.gz gctags.1.gz
mv etags.1.gz etags.emacs.1.gz
popd

mv %{buildroot}%{_infodir}/info.info.gz %{buildroot}%{_infodir}/info.gz

install -d %{buildroot}%{_datadir}/emacs/site-lisp/site-start.d

install -d %{buildroot}/%{_datadir}/pkgconfig
install -p -m 0644 emacs.pc %{buildroot}/%{_datadir}/pkgconfig

install -d %{buildroot}%{_rpmconfigdir}/macros.d
install -p -m 0644 macros.emacs %{buildroot}%{_rpmconfigdir}/macros.d/

rm -f %{buildroot}%{_infodir}/dir

install -d %{buildroot}%{_userunitdir}
install -p -m 0644 %SOURCE7 %{buildroot}%{_userunitdir}/emacs.service

# Emacs 26.1 don't installs the upstream unit file to /usr/lib64 on 64bit archs.
rm -f %{buildroot}/usr/lib64/systemd/user/emacs.service

rm -f *-filelist {common,el}-*-files

( TOPDIR=${PWD}
  cd %{buildroot}

  find .%{_datadir}/emacs/%{version}/lisp .%{_datadir}/emacs/%{version}/lisp/leim \
  .%{_datadir}/emacs/site-lisp \( -type f -name '*.elc' -fprint $TOPDIR/common-lisp-none-elc-files \) -o \( -type d -fprintf $TOPDIR/common-lisp-dir-files "%%%%dir %%p\n" \) -o \( -name '*.el.gz' -fprint $TOPDIR/el-bytecomped-files -o -fprint $TOPDIR/common-not-comped-files \)
)
sed -i -e "s|\.%{_prefix}|%{_prefix}|" *-files
cat common-*-files > common-filelist
cat el-*-files common-lisp-dir-files > el-filelist

%preun
%{_sbindir}/alternatives --remove emacs %{_bindir}/emacs-%{version}

%posttrans
%{_sbindir}/alternatives --install %{_bindir}/emacs emacs %{_bindir}/emacs-%{version} 80

%if !%{with bootstrap}
%preun lucid
%{_sbindir}/alternatives --remove emacs %{_bindir}/emacs-%{version}-lucid
%{_sbindir}/alternatives --remove emacs-lucid %{_bindir}/emacs-%{version}-lucid

%posttrans lucid
%{_sbindir}/alternatives --install %{_bindir}/emacs emacs %{_bindir}/emacs-%{version}-lucid 70
%{_sbindir}/alternatives --install %{_bindir}/emacs-lucid emacs-lucid %{_bindir}/emacs-%{version}-lucid 60
%endif

%preun nox
%{_sbindir}/alternatives --remove emacs %{_bindir}/emacs-%{version}-nox
%{_sbindir}/alternatives --remove emacs-nox %{_bindir}/emacs-%{version}-nox

%posttrans nox
%{_sbindir}/alternatives --install %{_bindir}/emacs emacs %{_bindir}/emacs-%{version}-nox 70
%{_sbindir}/alternatives --install %{_bindir}/emacs-nox emacs-nox %{_bindir}/emacs-%{version}-nox 60

%post common
for f in %{info_files}; do
  /sbin/install-info %{_infodir}/$f.info.gz %{_infodir}/dir 2> /dev/null || :
done

%preun common
%{_sbindir}/alternatives --remove emacs.etags %{_bindir}/etags.emacs
if [ "$1" = 0 ]; then
  for f in %{info_files}; do
    /sbin/install-info --delete %{_infodir}/$f.info.gz %{_infodir}/dir 2> /dev/null || :
  done
fi

%posttrans common
%{_sbindir}/alternatives --install %{_bindir}/etags emacs.etags %{_bindir}/etags.emacs 80 \
       --slave %{_mandir}/man1/etags.1.gz emacs.etags.man %{_mandir}/man1/etags.emacs.1.gz


%files
%defattr(-,root,root)
%doc doc/NEWS BUGS README
%license etc/COPYING
%attr(0755,-,-) %ghost %{_bindir}/emacs
%{_bindir}/emacs-%{version}
%{_datadir}/appdata/*
%{_datadir}/icons/hicolor/*
%{_datadir}/applications/emacs.desktop

%if !%{with bootstrap}
%files        lucid
%defattr(-,root,root)
%attr(0755,-,-) %ghost %{_bindir}/emacs
%attr(0755,-,-) %ghost %{_bindir}/emacs-lucid
%{_bindir}/emacs-%{version}-lucid
%endif

%files        nox
%defattr(-,root,root)
%attr(0755,-,-) %ghost %{_bindir}/emacs
%attr(0755,-,-) %ghost %{_bindir}/emacs-nox
%{_bindir}/emacs-%{version}-nox

%files        common -f common-filelist -f el-filelist
%defattr(-,root,root)
%doc doc/NEWS BUGS README
%license etc/COPYING
%{_rpmconfigdir}/macros.d/macros.emacs
%attr(0644,root,root) %config(noreplace) %{_datadir}/emacs/site-lisp/default.el
%attr(0644,root,root) %config %{_datadir}/emacs/site-lisp/site-start.el
%{_bindir}/gctags
%{_bindir}/ebrowse
%{_bindir}/emacsclient
%{_bindir}/etags.emacs
%{_libexecdir}/emacs
%{pkgconfig}/emacs.pc
%{_userunitdir}/emacs.service
%dir %{_datadir}/emacs/%{version}
%{_datadir}/emacs/%{version}/etc
%{_datadir}/emacs/%{version}/site-lisp
%{_infodir}/*

%files       filesystem
%defattr(-,root,root)
%dir %{_datadir}/emacs
%dir %{_datadir}/emacs/site-lisp
%dir %{_datadir}/emacs/site-lisp/site-start.d

%files       help
%defattr(-,root,root)
%doc doc/NEWS BUGS README
%{_mandir}/*/*
%{_infodir}/*

%changelog
* Sat Jan 11 2020 openEuler Buildteam <buildteam@openeuler.org> - 1:26.1-11
- remove unnecessary source

* Sat Dec 28 2019 openEuler Buildteam <buildteam@openeuler.org> - 1:26.1-10
- Type:bugfix
- ID:NA
- SUG:NA
- DESC:optimization the spec

* Tue Oct 29 2019 openEuler Buildteam <buildteam@openeuler.org> - 1:26.1-9
- Type:bugfix
- Id:NA
- SUG:NA
- DESC:change the pakcage list and requires

* Tue Oct 29 2019 yanglijin <yanglijin@huawei.com> - 1:26.1-8
- emacs can not use

* Fri Sep 20 2019 chenzhenyu <chenzhenyu13@huawei.com> - 1:26.1-7
- Package init
