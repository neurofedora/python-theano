%global pkgname Theano
#%%global rctag rc3

Name:           python-theano
Version:        0.6.0
Release:        5%{?rctag:.%{rctag}}%{?dist}
Summary:        Mathematical expressions involving multidimensional arrays

License:        BSD
URL:            http://deeplearning.net/software/theano/
Source0:        https://pypi.python.org/packages/source/T/%{pkgname}/%{pkgname}-%{version}%{?rctag:.%{rctag}}.tar.gz
# Files from git that were omitted from the release
Source1:        %{pkgname}-missing.tar.xz
# Images used when building documentation
Source2:        https://secure.travis-ci.org/Theano/Theano.png
Source3:        https://pypip.in/v/Theano/badge.png
# Renamed due to base name collision with source3.
# Original: https://pypip.in/d/Theano/badge.png
Source4:        badge2.png

# Fix some documentation bugs
Patch0:         %{name}-doc.patch
# Unbundle python-six
Patch1:         %{name}-six.patch
# Fix a build failure on arm due to an inverted test
Patch2:         %{name}-arm.patch

BuildArch:      noarch

BuildRequires:  atlas-devel
BuildRequires:  epydoc
BuildRequires:  numpy python3-numpy
BuildRequires:  pydot
BuildRequires:  python2-devel python3-devel
BuildRequires:  python-nose python3-nose
BuildRequires:  python-setuptools python3-setuptools
BuildRequires:  python-six python3-six
BuildRequires:  python-sphinx
BuildRequires:  scipy python3-scipy
BuildRequires:  tex-dvipng

Requires:       atlas-devel
Requires:       gcc-c++
Requires:       gcc-gfortran
Requires:       numpy
Requires:       pydot
Requires:       python-six
Requires:       scipy

%description
Theano is a Python library that allows you to define, optimize, and
evaluate mathematical expressions involving multi-dimensional arrays
efficiently.  Theano features:
- tight integration with NumPy: Use numpy.ndarray in Theano-compiled
  functions.
- transparent use of a GPU: Perform data-intensive calculations up to
  140x faster than with CPU.(float32 only)
- efficient symbolic differentiation: Theano does your derivatives for
  function with one or many inputs.
- speed and stability optimizations: Get the right answer for log(1+x)
  even when x is really tiny.
- dynamic C code generation: Evaluate expressions faster.
- extensive unit-testing and self-verification: Detect and diagnose many
  types of mistake.

%package doc
Summary:        Theano documentation

%description doc
User documentation for Theano.

%package -n python3-theano
Summary:        Mathematical expressions involving multidimensional arrays
Requires:       atlas-devel
Requires:       gcc-c++
Requires:       gcc-gfortran
Requires:       python3-numpy
Requires:       python3-scipy
Requires:       python3-six

%description -n python3-theano
Theano is a Python library that allows you to define, optimize, and
evaluate mathematical expressions involving multi-dimensional arrays
efficiently.  Theano features:
- tight integration with NumPy: Use numpy.ndarray in Theano-compiled
  functions.
- transparent use of a GPU: Perform data-intensive calculations up to
  140x faster than with CPU.(float32 only)
- efficient symbolic differentiation: Theano does your derivatives for
  function with one or many inputs.
- speed and stability optimizations: Get the right answer for log(1+x)
  even when x is really tiny.
- dynamic C code generation: Evaluate expressions faster.
- extensive unit-testing and self-verification: Detect and diagnose many
  types of mistake.

%prep
%setup -q -n %{pkgname}-%{version}%{?rctag:.%{rctag}}
%setup -q -n %{pkgname}-%{version}%{?rctag:.%{rctag}} -T -D -a 1
%patch0
%patch1
%patch2

# Don't use non-local images when building documentation
cp -p %{SOURCE2} %{SOURCE3} %{SOURCE4} doc/images
sed -e 's,https://.*/Theano\.png?branch=master,images/Theano.png,' \
    -e 's,https://pypip\.in/v/Theano/badge\.png,images/badge.png,' \
    -e 's,https://pypip\.in/d/Theano/badge\.png,images/badge2.png,' \
    -i doc/index.txt doc/install.txt

# Remove the packaged egg
rm -fr %{pkgname}.egg-info

# Remove bundled python-six
rm -f theano/compat/six.py

# Remove the shebang from a non-executable Python file
for fil in theano/sandbox/neighbourhoods.py; do
  sed '1d' $fil > $fil.new
  touch -r $fil $fil.new
  mv -f $fil.new $fil
done

# Prepare for python 3 build
cp -a . %{py3dir}

# We don't need to use /usr/bin/env
for fil in $(grep -FRl /usr/bin/env .); do
  sed 's,/usr/bin/env[[:blank:]]*python.*,/usr/bin/python2,' $fil > $fil.new
  touch -r $fil $fil.new
  chmod a+x $fil.new
  mv -f $fil.new $fil
done
for fil in $(grep -FRl /usr/bin/env %{py3dir}); do
  sed 's,/usr/bin/env[[:blank:]]*python.*,/usr/bin/python3,' $fil > $fil.new
  touch -r $fil $fil.new
  chmod a+x $fil.new
  mv -f $fil.new $fil
done

%build
# The python3 build fails with Unicode errors without this
export LC_ALL=en_US.UTF-8

# Python 2 build
python2 setup.py build

# Python 3 build
pushd %{py3dir}
python3 setup.py build
popd

# Build the documentation
export PYTHONPATH=$PWD
python2 doc/scripts/docgen.py --nopdf

# Remove build artifacts
rm -fr html/.buildinfo html/.doctrees

%install
# The python3 installation fails with Unicode errors without this
export LC_ALL=en_US.UTF-8

# Install python 2 build
python2 setup.py install -O1 --skip-build --root %{buildroot}

# Install python 3 build
pushd %{py3dir}
python3 setup.py install -O1 --skip-build --root %{buildroot}
popd

# Restore executable permission on the scripts
chmod a+x $(find %{buildroot} -name \*.py -o -name \*.sh | xargs grep -l '^#!')

# Theano's self tests currently fail one test.  Enable this once upstream has
# fixed the problem.
#
#%%check
#PYTHONPATH=$PWD bin/theano-test

%files
%doc DESCRIPTION.txt HISTORY.txt NEWS.txt README.txt
%license doc/LICENSE.txt
%{python2_sitelib}/*

%files doc
%doc html

%files -n python3-theano
%doc DESCRIPTION.txt HISTORY.txt NEWS.txt README.txt
%license doc/LICENSE.txt
%{_bindir}/theano-*
%{python3_sitelib}/*

%changelog
* Sat Feb 21 2015 Jerry James <loganjerry@gmail.com> - 0.6.0-5
- Add -arm patch to fix build failure on arm builders due to inverted test

* Sat Feb 21 2015 Jerry James <loganjerry@gmail.com> - 0.6.0-4
- Drop workaround for fixed bug (bz 1075826)
- Use license macro

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.6.0-3.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed May 14 2014 Jerry James <loganjerry@gmail.com> - 0.6.0-3
- Rebuild for https://fedoraproject.org/wiki/Changes/Python_3.4

* Thu Mar 13 2014 Jerry James <loganjerry@gmail.com> - 0.6.0-2
- Add python3 subpackage
- Add another icon to the -missing tarball
- Update source icons
- Unbundle python-six
- Add workaround for bz 1075826

* Sat Dec  7 2013 Jerry James <loganjerry@gmail.com> - 0.6.0-1
- New upstream release
- Drop upstreamed -import patch

* Mon Oct 21 2013 Jerry James <loganjerry@gmail.com> - 0.6.0-0.1.rc3
- Add the -import patch to fix an exception
- Add more files to the base package docs

* Tue Aug 27 2013 Jerry James <loganjerry@gmail.com> - 0.6.0-0.rc3
- Initial RPM
