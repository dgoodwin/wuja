%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: wuja
Version: 0.0.8
Release:        1%{?dist}
Summary: Gnome desktop applet for integration with Google Calendar

Group: Applications/Internet
License: GPL
URL: http://dangerouslyinc.com/wuja
Source0: http://dangerouslyinc.com/files/wuja/wuja-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch
BuildRequires: python-devel

Requires: python-vobject >= 0.4.4
Requires: python-dateutil >= 1.1
Requires: gnome-python2-libegg >= 2.14.3
Requires: gnome-python2-gconf >= 2.18.1
Requires: notify-python >= 0.1.0

Requires(pre): GConf2
Requires(post): GConf2
Requires(preun): GConf2

%description
wuja is a Gnome application for integration with Google Calendar.
%prep
%setup -q -n wuja-%{version}


%build
%{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{python_sitelib}/*egg-info/requires.txt


%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule \
        %{_sysconfdir}/gconf/schemas/wuja.schema >/dev/null || :
fi


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
* Sat Jun 02 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.8-1
- Releasing 0.0.8.

* Sun Apr 29 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.7-2
- Updating spec file as per Fedora review suggestions.

* Thu Apr 26 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.7-1
- Updated to use _elementtree module in Python 2.5 if available.

* Mon Feb 22 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.6-1
- Renamed back to just wuja, not really a Gnome applet.

* Mon Feb 05 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.6-1
- Disabled threading for temporary bugfix release.

* Mon Feb 05 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.5-3
- Updates to .spec file.

* Sun Jan 21 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.5-2
- Renamed to gnome-applet-wuja.

* Wed Jan 17 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.5-1
- Initial packaging.

