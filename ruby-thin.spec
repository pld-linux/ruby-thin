#
# Conditional build:
%bcond_with	tests		# build without tests

%define	pkgname thin
Summary:	A thin and fast web server
Name:		ruby-%{pkgname}
Version:	1.5.0
Release:	1
License:	(GPL v2 or Ruby) and MIT
Group:		Development/Languages
Source0:	http://rubygems.org/gems/%{pkgname}-%{version}.gem
# Source0-md5:	2f011aba841da210e49d09b85130dfc0
# git clone https://github.com/macournoyer/thin.git && cd thin && git checkout v1.5.0
# tar czvf thin-1.5.0-tests.tgz spec/
Source1:	http://pkgs.fedoraproject.org/repo/pkgs/rubygem-thin/thin-%{version}-tests.tgz/d7ee25c7f947151b93501668c53e2d34/thin-%{version}-tests.tgz
# Source1-md5:	d7ee25c7f947151b93501668c53e2d34
# https://github.com/macournoyer/thin/issues/77
Patch1:		remove-rspec1-require.patch
Patch2:		rspec2-null-object.patch
# https://github.com/macournoyer/thin/issues/76
Patch3:		fix-install-spec.patch
URL:		http://code.macournoyer.com/thin/
BuildRequires:	rpm-rubyprov
BuildRequires:	rpmbuild(macros) >= 1.656
BuildRequires:	ruby-devel
BuildRequires:	sed >= 4.0
%if %{with tests}
BuildRequires:	ruby-daemons >= 1.0.9
BuildRequires:	ruby-eventmachine >= 0.12.6
BuildRequires:	ruby-rack >= 1.0.0
BuildRequires:	ruby-rspec
%endif
Requires:	curl
Requires:	ruby-daemons >= 1.0.9
Requires:	ruby-eventmachine >= 0.12.6
Requires:	ruby-rack >= 1.0.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Thin is a Ruby web server that glues together three of the best Ruby
libraries in web history. The Mongrel parser, the root of Mongrel
speed and security, Event Machine, a network I/O library with
extremely high scalability and Rack, a minimal interface between
webservers and Ruby frameworks.

%package doc
Summary:	Documentation for %{name}
Group:		Documentation
Requires:	%{name} = %{version}-%{release}

%description doc
Documentation for %{name}.

%prep
%setup -q -n %{pkgname}-%{version} -a1
%{__sed} -i -e '1 s,#!.*ruby,#!%{__ruby},' bin/*
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
cd ext/thin_parser
%{__ruby} extconf.rb
%{__make} \
	CC="%{__cc}" \
	LDFLAGS="%{rpmldflags}" \
	CFLAGS="%{rpmcflags} -fPIC"

%if %{with tests}
# Depends on rubygem-benchmark_unit, not available in Fedora yet.
rm -rf spec/perf
# Test fails.
# https://github.com/macournoyer/thin/issues/40
rm -f spec/server/pipelining_spec.rb
# The 'should force kill process in pid file' spec is not compatible with RSpec2.
# https://github.com/rspec/rspec-core/issues/520
# http://rubyforge.org/tracker/?func=detail&aid=29450&group_id=524&atid=2086
ruby -ne "print unless (99..117).include? $." spec/daemonizing_spec.rb > spec/daemonizing_spec.rb

rspec spec
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{ruby_vendorlibdir},%{_bindir}}
cp -a lib/* $RPM_BUILD_ROOT%{ruby_vendorlibdir}
cp -a bin/* $RPM_BUILD_ROOT%{_bindir}

# install ext
install -d $RPM_BUILD_ROOT%{ruby_vendorarchdir}
install -p ext/thin_parser/thin_parser.so $RPM_BUILD_ROOT%{ruby_vendorarchdir}

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_bindir}/thin
%{ruby_vendorlibdir}/thin
%{ruby_vendorlibdir}/thin.rb
%attr(755,root,root) %{ruby_vendorarchdir}/thin_parser.so

# rack adapter
%dir %{ruby_vendorlibdir}/rack/adapter
%{ruby_vendorlibdir}/rack/adapter/loader.rb
%{ruby_vendorlibdir}/rack/adapter/rails.rb
