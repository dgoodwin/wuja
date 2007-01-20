%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name: wuja
Version: 0.0.5
Release:        1%{?dist}
Summary: Gnome desktop applet for integration with Google Calendar

Group: Applications/Internet
License: GPL
URL: http://dangerouslyinc.com/wuja
Source0: http://dangerouslyinc.com/files/wuja/wuja-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch: noarch
Requires: python-vobject >= 0.4.4, python-dateutil >= 1.1, python-elementtree >= 1.2.6

%description
wuja is a Gnome desktop applet for integration with Google Calendar.
%prep
%setup -q -n %{name}-%{version}


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT
rm -f $RPM_BUILD_ROOT%{python_sitelib}/*egg-info/requires.txt


%clean
rm -rf $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%doc AUTHORS
%doc LICENSE
%doc README
%dir %{python_sitelib}/wuja
%dir %{python_sitelib}/wuja/data

/etc/gconf/schemas/wuja.schema
/usr/bin/wuja
%{python_sitelib}/wuja/calendar.py
%{python_sitelib}/wuja/calendar.pyc
%{python_sitelib}/wuja/calendar.pyo
%{python_sitelib}/wuja/log.py
%{python_sitelib}/wuja/log.pyc
%{python_sitelib}/wuja/log.pyo
%{python_sitelib}/wuja/model.py
%{python_sitelib}/wuja/model.pyc
%{python_sitelib}/wuja/model.pyo
%{python_sitelib}/wuja/preferences.py
%{python_sitelib}/wuja/preferences.pyc
%{python_sitelib}/wuja/preferences.pyo
%{python_sitelib}/wuja/utils.py
%{python_sitelib}/wuja/utils.pyc
%{python_sitelib}/wuja/utils.pyo
%{python_sitelib}/wuja/notifier.py
%{python_sitelib}/wuja/notifier.pyc
%{python_sitelib}/wuja/notifier.pyo
%{python_sitelib}/wuja/upgrade.py
%{python_sitelib}/wuja/upgrade.pyc
%{python_sitelib}/wuja/upgrade.pyo
%{python_sitelib}/wuja/config.py
%{python_sitelib}/wuja/config.pyc
%{python_sitelib}/wuja/config.pyo
%{python_sitelib}/wuja/data.py
%{python_sitelib}/wuja/data.pyc
%{python_sitelib}/wuja/data.pyo
%{python_sitelib}/wuja/feed.py
%{python_sitelib}/wuja/feed.pyc
%{python_sitelib}/wuja/feed.pyo
%{python_sitelib}/wuja/decorators.py
%{python_sitelib}/wuja/decorators.pyc
%{python_sitelib}/wuja/decorators.pyo
%{python_sitelib}/wuja/application.py
%{python_sitelib}/wuja/application.pyc
%{python_sitelib}/wuja/application.pyo
%{python_sitelib}/wuja/__init__.py
%{python_sitelib}/wuja/__init__.pyc
%{python_sitelib}/wuja/__init__.pyo

%{python_sitelib}/wuja/data/wuja-icon-128x128.png
%{python_sitelib}/wuja/data/calendar.glade
%{python_sitelib}/wuja/data/wuja-prefs.glade
%{python_sitelib}/wuja/data/wuja-about.glade
%{python_sitelib}/wuja/data/wuja-menu.xml
%{python_sitelib}/wuja/data/alert-window.glade
%{python_sitelib}/wuja/data/wuja-icon-24x24.png

%changelog
* Wed Jan 17 2007 Devan Goodwin <dgoodwin@dangerouslyinc.com> 0.0.5-1
- Initial packaging.

