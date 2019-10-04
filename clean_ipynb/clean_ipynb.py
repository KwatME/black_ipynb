from json import dump, load
from shutil import copyfile

from .clean_julia_code import clean_julia_code
from .clean_python_code import clean_python_code
from .has_julia_and_juliaformatter import has_julia_and_juliaformatter


def clean_ipynb(ipynb_file_path, overwrite):
    """Clean a Jupyter notebook.

    Cleaning Python notebooks is supported out of the box, but Julia notebooks require
    installation of Julia and JuliaFormatter.jl.

    Args:
        ipynb_file_path (str): Path to the notebook.
        overwrite (bool): True to overwrite the existing notebook, False to write the
            formatted output to file [orig_name].ipynb -> [orig_name].cleaned.ipynb.

    Returns: None if successful, 1 if formatting could not be carried out. This could
    be the case if prerequisites for Julia formatting have not been met, but a Julia
    notebook is given.

    """
    if not overwrite:

        ipynb_file_path = copyfile(
            ipynb_file_path, ipynb_file_path.replace(".ipynb", ".cleaned.ipynb")
        )

    with open(ipynb_file_path) as io:

        ipynb_dict = load(io)

    language = ipynb_dict["metadata"]["language_info"]["name"]

    can_clean_julia_code = has_julia_and_juliaformatter()

    if language == "python":

        clean_code = clean_python_code

    elif language == "julia" and can_clean_julia_code:

        clean_code = clean_julia_code

    else:
        # If nothing can be cleaned, output the original file and return with code 1.

        with open(ipynb_file_path, mode="w") as io:

            dump(ipynb_dict, io, indent=1)

            io.write("\n")

        return 1

    cells = []

    for cell_dict in ipynb_dict["cells"]:

        cell_dict["execution_count"] = None

        cell_dict["outputs"] = []

        if (
            "metadata" in cell_dict
            and "jupyter" in cell_dict["metadata"]
            and "source_hidden" in cell_dict["metadata"]["jupyter"]
        ):

            cell_dict["metadata"]["jupyter"].pop("source_hidden")

        if cell_dict["cell_type"] == "code":

            source_join_clean_split = clean_code("".join(cell_dict["source"])).split(
                sep="\n"
            )

            if len(source_join_clean_split) == 1 and source_join_clean_split[0] == "":

                continue

            source_join_clean_split[:-1] = [
                "{}\n".format(line) for line in source_join_clean_split[:-1]
            ]

            cell_dict["source"] = source_join_clean_split

        cells.append(cell_dict)

    ipynb_dict["cells"] = cells

    with open(ipynb_file_path, mode="w") as io:

        dump(ipynb_dict, io, indent=1)

        io.write("\n")
