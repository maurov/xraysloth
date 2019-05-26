
.. _data-model:

Notes on the data model
=======================

Preface
-------

Every application has to deal with data and organize them internally following a
model. A lot of effort is put in this application in order to follow current
standards in data formats and build a model that mimics those formats.

Currently, the standard data format is `HDF5 <https://www.hdfgroup.org/>`_. This
is extremely generic. In a very simple picture, this is a binary format that
store the data like files and directories in your operative system. Thus, it is
naturally hierarchical. The two key concepts in this data format are the
**group** and **dataset**. A group is like a directory, while a dataset is like
a file. That's all.

In Python, the library that permits dealing with HDF5 files is `h5py
<https://www.h5py.org/>`_. This library is very generic and is better to use
another library that builds on top of it to interact with HDF5. Here the choice
is to use `SILX <http://www.silx.org/>_`.

As HDF5 is very generic, data inside it can be stored in whatever way. For this reason, synchrotron radiation and nuclear large scale facilities have decided to adopt some conventions. These conventions (also known as *definitions*) are represented by the `NeXus data format <https://www.nexusformat.org/>`_. This is the standard toward our data model is going. Nevertheless, in practice NeXus is not easy to understand and use...

Introduction
------------

The scope of this document is to describe how the data, from a HDF5 source are
loaded (= read) in the computer memory, processed, generated other data and
finally write back to HDF5. This process is not easy and extremely time
consuming in the design, especially when on top of it there is the need to put a GUI (graphical user interface).

Here **data model** refers to the model part in the `model-view-controller
<https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller>`_
architecture. With simple words, the model is what is responsible of handling
data.

The architecture of the current data model is based on SILX and Qt. The
Qt-related part is kept as much separated as possible from the data model in
order to have the possibility to build the model without Qt, which is mainly
responsible for the GUI part. This is dictated by the necessity to let use the
model also from other applications using another graphical backend (e.g. Wx) or
without a graphical backend at all when a batch processing is required.

.. note:: Since HDF5 is naturally hierarchical, the data model is naturally
  hierarchical, that is, it will have a tree-like structure. For this reason, the *parent/child* structure is present in each object.

From Spec files to HDF5
-----------------------

At the origin there was a good and simple ASCII format, the Spec file.
