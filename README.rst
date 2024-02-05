========
Overview
========



.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs| |readthedocs|
    * - build status
      - |testing| |codestyle| |coverage|

.. |docs| image:: https://github.com/HERMES-SOC/hermes_eea/actions/workflows/docs.yml/badge.svg
    :target: https://github.com/HERMES-SOC/hermes_eea/actions/workflows/docs.yml
    :alt: Documentation Build Status

.. |testing| image:: https://github.com/HERMES-SOC/hermes_eea/actions/workflows/testing.yml/badge.svg
    :target: https://github.com/HERMES-SOC/hermes_eea/actions/workflows/testing.yml
    :alt: Build Status

.. |coverage| image:: https://codecov.io/gh/HERMES-SOC/hermes_eea/branch/main/graph/badge.svg?token=PSEF942JD2 
    :target: https://codecov.io/gh/HERMES-SOC/hermes_eea

.. |codestyle| image:: https://github.com/HERMES-SOC/hermes_eea/actions/workflows/codestyle.yml/badge.svg
    :target: https://github.com/HERMES-SOC/hermes_eea/actions/workflows/codestyle.yml
    :alt: Codestyle and linting using flake8

.. |readthedocs| image:: https://readthedocs.org/projects/hermes-eea/badge/?version=latest
    :target: https://hermes-eea.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. end-badges

This is a Python package for processing and analyzing data from the Electron Electrostatic Analyzer (EEA) instrument on the Lunar Gateway.
The EEA provides measurements of low-energy electrons in the solar wind and in Earth’s deep magnetotail by measuring electron flux as functions of energy and direction.


Testing Calibration Code in Pull Requests
------------------------------------------
Our CI/CD Pipeline is designed to validate the functionality of the calibration code within pull requests. Upon initiation, the pipeline executes the calibration code and verifies its successful operation without any errors. A successful execution results in the pipeline passing, and it automatically posts a comment on the pull request detailing the outcomes.

The comment will include a zip file containing both the original and the calibrated versions of the file used in the process.

For calibration, the pipeline relies on binary files located in the data directory. To test the calibration code with a new binary file, simply replace the existing test file in the data directory and submit a new pull request. The pipeline will then apply the calibration code to this new file.

For comprehensive guidelines on testing the calibration code within our CI/CD framework, please read the `Workflow for Maintainers Documentation <https://hermes-eea.readthedocs.io/en/latest/dev-guide/maintainer_workflow.html>`.


License
-------

This project is Copyright (c) Jane Doe and licensed under
the terms of the BSD 3-Clause "New" or "Revised" License license. This package is based upon
the `Openastronomy packaging guide <https://github.com/OpenAstronomy/packaging-guide>`_
which is licensed under the BSD 3-clause licence. See the LICENSE file for
more information.


Contributing
------------

We love contributions! hermes_eea is open source,
built on open source, and we'd love to have you hang out in our community.

**Imposter syndrome disclaimer**: We want your help. No, really.

There may be a little voice inside your head that is telling you that you're not
ready to be an open source contributor; that your skills aren't nearly good
enough to contribute. What could you possibly offer a project like this one?

We assure you - the little voice in your head is wrong. If you can write code at
all, you can contribute code to open source. Contributing to open source
projects is a fantastic way to advance one's coding skills. Writing perfect code
isn't the measure of a good developer (that would disqualify all of us!); it's
trying to create something, making mistakes, and learning from those
mistakes. That's how we all improve, and we are happy to help others learn.

Being an open source contributor doesn't just mean writing code, either. You can
help out by writing documentation, tests, or even giving feedback about the
project (and yes - that includes giving feedback about the contribution
process). Some of these contributions may be the most valuable to the project as
a whole, because you're coming to the project with fresh eyes, so you can see
the errors and assumptions that seasoned contributors have glossed over.

Note: This disclaimer was originally written by
`Adrienne Lowe <https://github.com/adriennefriend>`_ for a
`PyCon talk <https://www.youtube.com/watch?v=6Uj746j9Heo>`_, and was adapted by
hermes_eea based on its use in the README file for the
`MetPy project <https://github.com/Unidata/MetPy>`_.

Code of Conduct
---------------
When you are interacting with the HERMES-SOC community you are asked to follow
our `Code of Conduct <https://github.com/HERMES-SOC/code-of-conduct/blob/main/CODE_OF_CONDUCT.md>`_.

Acknowledgements
----------------
The package template used by this package is based on the one developed by the
`OpenAstronomy community <https://openastronomy.org>`_ and the `SunPy Project <https://sunpy.org/>`_.
