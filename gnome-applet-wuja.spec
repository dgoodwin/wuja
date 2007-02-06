%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: gnome-applet-wuja
Version: 0.0.6
Release:        1%{?dist}
Summary: Gnome desktop applet for integration with Google Calendar

Group: Applications/Internet
License: GPL
URL: http://dangerouslyinc.com/wuja
Source0: http://dangerouslyinc.com/files/wuja/wuja-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch

Requires: python-vobject >= 0.4.4
Requires: python-dateutil >= 1.1
Requires: python-elementtree >= 1.2.6

Requires(pre): GConf2
Requires(post): GConf2
Requires(preun): GConf2

Provides: wuja = %{version}-%{release}

%description
gnome-applet-wuja is a Gnome desktop applet for integration with Google Calendar.
%prep
%setup -q -n wuja-%{version}


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
        %{_sysconfdir}/gconf/schemas/wuja.schema >/dev/null || :
fi


%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{python_sitelib}/*egg-info/requires.txt


%post
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule \
    %{_sysconfdir}/gconf/schemas/wuja.schema > /dev/null || :


%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
        %{_sysconfdir}/gconf/schemas/wuja.schema > /dev/null || :
fi


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS
%doc LICENSE
%doc README
%{_sysconfdir}/gconf/schemas/wuja.schema
%{_bindir}/wuja
%dir %{python_sitelib}/wuja
%{python_sitelib}/wuja/*


%changelog
* Mon Feb 05 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.6-1
- Disabled threading for temporary bugfix release.

* Mon Feb 05 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.5-3
- Updates to .spec file.

* Sun Jan 21 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.5-2
- Renamed to gnome-applet-wuja.

* Wed Jan 17 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.5-1
- Initial packaging.

