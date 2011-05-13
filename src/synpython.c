#include <Python.h>
#include "edge.h"
#include "node.h"
#include "network.h"
#include "histogram2d.h"


static PyObject *pysyn_create_net(PyObject *self, PyObject *args)
{
    syn_net *net = syn_create_net();
    PyObject *result = Py_BuildValue("i", (long)net);
    
    return result;
}

static PyObject *pysyn_destroy_net(PyObject *self, PyObject *args)
{
    long p;
    syn_net *net;

    if (PyArg_ParseTuple(args, "i", &p)) {
      net = (syn_net *)p;
      syn_destroy_net(net);
    }
    
    PyObject *result = Py_BuildValue("");
    return result;
}

static PyObject *pysyn_add_node(PyObject *self, PyObject *args)
{
    long p;
    unsigned int type;
    syn_net *net;
    syn_node *node = NULL;

    if (PyArg_ParseTuple(args, "ii", &p, &type)) {
      net = (syn_net *)p;
      node = syn_add_node(net, type);
    }

    PyObject *result = Py_BuildValue("i", (long)node);
    return result;
}

static PyObject *pysyn_add_edge_to_net(PyObject *self, PyObject *args)
{
    long p1, p2, p3;
    syn_net *net;
    syn_node *orig, *targ;
    int res = 0;

    if (PyArg_ParseTuple(args, "iii", &p1, &p2, &p3)) {
      net = (syn_net *)p1;
      orig = (syn_node *)p2;
      targ = (syn_node *)p3;
      res = syn_add_edge_to_net(net, orig, targ);
    }

    PyObject *result = Py_BuildValue("b", res);
    return result;
}

static PyObject *pysyn_compute_evc(PyObject *self, PyObject *args)
{
    long p;
    syn_net *net;

    if (PyArg_ParseTuple(args, "i", &p)) {
      net = (syn_net *)p;
      syn_compute_evc(net);
    }
    
    PyObject *result = Py_BuildValue("");
    return result;
}

static PyObject *pysyn_write_evc(PyObject *self, PyObject *args)
{
    long p;
    char *file_path;
    syn_net *net;

    if (PyArg_ParseTuple(args, "is", &p, &file_path)) {
      net = (syn_net *)p;
      syn_write_evc(net, file_path);
    }
    
    PyObject *result = Py_BuildValue("");
    return result;
}

static PyObject *pysyn_print_net_info(PyObject *self, PyObject *args)
{
    long p;
    syn_net *net;

    if (PyArg_ParseTuple(args, "i", &p)) {
      net = (syn_net *)p;
      syn_print_net_info(net);
    }
    
    PyObject *result = Py_BuildValue("");
    return result;
}

static PyObject *pysyn_get_evc_histogram(PyObject *self, PyObject *args)
{
    long p;
    int bin_number;
    syn_net *net;
    syn_histogram2d *hist = NULL;

    if (PyArg_ParseTuple(args, "ii", &p, &bin_number)) {
      net = (syn_net *)p;
      hist = syn_get_evc_histogram(net, bin_number);
    }
    
    PyObject *result = Py_BuildValue("i", (long)hist);
    return result;
}

static PyObject *pysyn_histogram2d_print(PyObject *self, PyObject *args)
{
    long p;
    syn_histogram2d *hist = NULL;

    if (PyArg_ParseTuple(args, "i", &p)) {
      hist = (syn_histogram2d *)p;
      syn_histogram2d_print(hist);
    }
    
    PyObject *result = Py_BuildValue("");
    return result;
}

static PyObject *pysyn_histogram2d_bin_number(PyObject *self, PyObject *args)
{
    long p;
    syn_histogram2d *hist = NULL;

    if (PyArg_ParseTuple(args, "i", &p)) {
      hist = (syn_histogram2d *)p;
    }
    
    PyObject *result = Py_BuildValue("i", hist->bin_number);
    return result;
}

static PyObject *pysyn_histogram2d_get_value(PyObject *self, PyObject *args)
{
    long p;
    int x, y;
    syn_histogram2d *hist = NULL;
    double value = 0.0;

    if (PyArg_ParseTuple(args, "iii", &p, &x, &y)) {
      hist = (syn_histogram2d *)p;
      value = syn_histogram2d_get_value(hist, x, y);
    }
    
    PyObject *result = Py_BuildValue("f", value);
    return result;
}

static PyMethodDef methods[] = {
    {"create_net", pysyn_create_net, METH_VARARGS, "Create network."},
    {"destroy_net", pysyn_destroy_net, METH_VARARGS, "Destroy network."},
    {"add_node", pysyn_add_node, METH_VARARGS, "Add node to network."},
    {"add_edge_to_net", pysyn_add_edge_to_net, METH_VARARGS, "Add edge to network."},
    {"compute_evc", pysyn_compute_evc, METH_VARARGS, "Compute EVC."},
    {"write_evc", pysyn_write_evc, METH_VARARGS, "Write EVC."},
    {"print_net_info", pysyn_print_net_info, METH_VARARGS, "Print net info."},
    {"get_evc_histogram", pysyn_get_evc_histogram, METH_VARARGS, "Get EVC histogram from net."},
    {"histogram2d_print", pysyn_histogram2d_print, METH_VARARGS, "Print histogram."},
    {"histogram2d_bin_number", pysyn_histogram2d_bin_number, METH_VARARGS, "Return histogram bin number."},
    {"histogram2d_get_value", pysyn_histogram2d_get_value, METH_VARARGS, "Return histogram bin value."},
    {NULL, NULL, 0, NULL},
};

PyMODINIT_FUNC initcore(void)
{
    Py_InitModule("core", methods);
}

