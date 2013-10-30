%global pkgname Theano
%global rctag rc3

Name:           python-theano
Version:        0.6.0
Release:        0.1%{?rctag:.%{rctag}}%{?dist}
Summary:        Mathematical expressions involving multidimensional arrays

License:        BSD
URL:            http://deeplearning.net/software/theano/
Source0:        https://pypi.python.org/packages/source/T/%{pkgname}/%{pkgname}-%{version}%{rctag}.tar.gz
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
# Insert a missing import
Patch1:         %{name}-import.patch

BuildArch:      noarch

BuildRequires:  atlas-devel
BuildRequires:  epydoc
BuildRequires:  numpy
BuildRequires:  pydot
BuildRequires:  python2-devel
BuildRequires:  python-nose
BuildRequires:  python-setuptools
BuildRequires:  python-sphinx
BuildRequires:  scipy
BuildRequires:  tex-dvipng

Requires:       atlas-devel
Requires:       gcc-c++
Requires:       gcc-gfortran
Requires:       numpy
Requires:       pydot
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

%prep
%setup -q -n %{pkgname}-%{version}%{rctag}
%setup -q -n %{pkgname}-%{version}%{rctag} -T -D -a 1
%patch0
%patch1

# Don't use non-local images when building documentation
cp -p %{SOURCE2} %{SOURCE3} %{SOURCE4} doc/images
sed -e 's,https://.*/Theano\.png?branch=master,images/Theano.png,' \
    -e 's,https://pypip\.in/v/Theano/badge\.png,images/badge.png,' \
    -e 's,https://pypip\.in/d/Theano/badge\.png,images/badge2.png,' \
    -i doc/index.txt doc/install.txt

# Remove the packaged egg
rm -fr %{pkgname}.egg-info

# Remove the shebang from a non-executable Python file
for fil in theano/sandbox/neighbourhoods.py; do
  sed '1,2d' $fil > $fil.new
  touch -r $fil $fil.new
  mv -f $fil.new $fil
done

# We don't need to use /usr/bin/env
for fil in $(grep -FRl /usr/bin/env .); do
  sed 's,/usr/bin/env[[:blank:]]*python.*,/usr/bin/python,' $fil > $fil.new
  touch -r $fil $fil.new
  chmod a+x $fil.new
  mv -f $fil.new $fil
done

%build
python setup.py build

# Build the documentation
export PYTHONPATH=$PWD
python doc/scripts/docgen.py --nopdf

# Remove build artifacts
rm -fr html/.buildinfo html/.doctrees

%install
python setup.py install -O1 --skip-build --root %{buildroot}

# Restore executable permission on the scripts
chmod a+x $(find %{buildroot} -name \*.py -o -name \*.sh | xargs grep -l '^#!')

# Theano's self tests currently fail one test.  Enable this once upstream has
# fixed the problem.
#
# %%check
# PYTHONPATH=$PWD bin/theano-test

%files
%doc doc/LICENSE.txt DESCRIPTION.txt HISTORY.txt NEWS.txt README.txt
%{_bindir}/theano-*
%{python_sitelib}/*

%files doc
%doc html

%changelog
* Mon Oct 21 2013 Jerry James <loganjerry@gmail.com> - 0.6.0-0.1.rc3
- Add the -import patch to fix an exception
- Add more files to the base package docs

* Tue Aug 27 2013 Jerry James <loganjerry@gmail.com> - 0.6.0-0.rc3
- Initial RPM
