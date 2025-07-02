#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Mon Feb  19 15:00:00 2024

@author: Luigi Sante Zampa (OGS)
@description: A set of functions to create and manage sbatch files on cineca HPC systems.
"""

# -----------------------------------------------------------------------------
import os
import time as Time
import shutil
import sys
import numpy as np
import psutil

# s : system separator
s = os.sep

# -----------------------------------------------------------------------------
def print_file( path_name ) :
    """
    Prints the contents of a file.

    Args:
        path_name (str): The path of the file to be printed.
    """

    with open( path_name, "r") as f :
        print( f.read() )

    f.close()

# -----------------------------------------------------------------------------
def is_cineca_system():
    """
    Check if the current environment is a Cineca system.

    This function checks for the presence of specific environment variables
    that are typically set on Cineca systems. If any of these environment
    variables are found, the function returns True, indicating that the
    current environment is a Cineca system.

    Returns:
        bool: True if the current environment is a Cineca system, False otherwise.
    """

    cineca_vars = ['CINECA_SCRATCH', 'CINECA_ENV']

    return any(var in os.environ for var in cineca_vars)


# -----------------------------------------------------------------------------
def create_sbatch_file( path, filename="run_slurm.bat", 
                        nodes=1, ntasks=1, ncpus=1, 
                        mem=50000, time="1:00:00", 
                        out= "logs/job.out", 
                        err= "logs/job.err", 
                        account="OGS23_PRACE_IT",
                        partition="g100_usr_prod",
                        mail_type="ALL",
                        mail_user="lzampa@ogs.it",
                        printf=False,
                        other_lines='',
                        job='',
                        run=False ) :
    """
    Create an sbatch file with the specified parameters.

    Args:
        - path (str): The path where the sbatch file will be created.
        - filename (str, optional): The name of the sbatch file. Defaults to "run.bat".
        - nodes (int, optional): The number of nodes. Defaults to 1.
        - ntasks (int, optional): The number of tasks. Defaults to 1.
        - ncpus (int, optional): The number of CPUs per task. Defaults to 1.
        - mem (int, optional): The memory in MB. Defaults to 50000.
        - time (str, optional): The time limit for the job. Defaults to "1:00:00".
        - out (str, optional): The path to the output file. Defaults to "logs/job.out".
        - err (str, optional): The path to the error file. Defaults to "logs/job.err".
        - account (str, optional): The account to be used. Defaults to "IscrC_GPS-MAST".
        - partition (str, optional): The partition to be used. Defaults to "g100_usr_prod".
        - mail_type (str, optional): The type of email notifications. Defaults to "ALL".
        - mail_user (str, optional): The email address to receive notifications. Defaults to "lzampa@ogs.it".
        - print (bool, optional): Whether to print the contents of the sbatch file. Defaults to False.
        - job (str, optional): The job to be executed. Defaults to ''.
        - run (bool, optional): Whether to submit the job to the queue. Defaults to False.

    Returns:
        str: The path of the sbatch file.
    """

    # Check if the directory specified by 'path' exists
    if os.path.exists( path ) == False :
        # If not, create the directory
        os.makedirs( path, exist_ok=True )
    
    # Create local directories for the output and error files
    logs_dir_out = os.path.dirname(out).split( os.sep )[-1]
    logs_dir_err = os.path.dirname(err).split( os.sep )[-1]

    if not os.path.exists( path +os.sep + logs_dir_out ):
        os.makedirs( path +os.sep + logs_dir_out, exist_ok=True )
    else :
        shutil.rmtree( path +os.sep + logs_dir_out )
        os.makedirs( path +os.sep + logs_dir_out, exist_ok=True )

    if not os.path.exists(path +os.sep + logs_dir_err):
        os.makedirs( path +os.sep + logs_dir_err, exist_ok=True )
    else :
        shutil.rmtree( path +os.sep + logs_dir_err )
        os.makedirs( path +os.sep + logs_dir_err, exist_ok=True )

    # Open a file at the specified path with write permissions
    with open( path +s+ filename, "w") as f :
        # Write the shebang line for a bash script
        f.write("#!/bin/bash\n\n")
        # Write the SLURM directives for the job resources
        f.write(f"#SBATCH --nodes={nodes}\n")
        f.write(f"#SBATCH --ntasks={ntasks}\n") 
        f.write(f"#SBATCH --cpus-per-task={ncpus}\n")
        f.write(f"#SBATCH --time {time}\n")
        f.write(f"#SBATCH --mem={mem}\n")
        f.write(f"#SBATCH --out {out}\n")
        f.write(f"#SBATCH --err {err}\n")
        f.write(f"#SBATCH --account={account}\n")
        f.write(f"#SBATCH --partition {partition} # partition to be used Galileo and debug queue\n")
        f.write(f"#SBATCH --mail-type={mail_type}\n")
        f.write(f"#SBATCH --mail-user={mail_user}\n")
        f.write("\n")
        # Write the job to be executed
        f.write("# main code\n")
        if ( type( other_lines ) == str ) and ( other_lines != '' ) :
            f.write(f"{other_lines}")
        if ( type( other_lines ) in ( list, tuple ) ) and ( not other_lines is False):
            for line in other_lines :
                f.write(f"{line}\n")
        f.write(job)
        f.write("\n")

    # If the 'printf' flag is True, print the contents of the file
    if printf == True :
        print( "\n# ---------------------------------------------------------" )
        print( path +s+ filename )
        print( "CONTENT :\n" )
        print_file( path +s+ filename )

    # Close the file
    f.close()

    # If the 'run' flag is True, submit the job to the queue
    if run == True :
        os.system( f"sbatch {path +s+ filename} &" )

    return path +s+ filename

# -----------------------------------------------------------------------------
def parfor( loop, 
            path, 
            chunks=2, 
            chunk_size=None,
            modules=[], 
            alias=[], 
            run=False, 
            add_time=False,
            printf=False, 
            filename="run_slurm.bat",
            nodes=1, 
            ntasks=1, 
            ncpus=1, 
            mem=50000, 
            time="1:00:00", 
            out= "logs/job.%a.out", 
            err= "logs/job.%a.err", 
            account="OGS23_PRACE_IT",
            partition="g100_usr_prod",
            mail_type="ALL",
            mail_user="lzampa@ogs.it",
            other_lines='', 
            ifor=0,
            readme_file_name="README_2_RUN" ) :
    
    """
    Generate a simple parallelized version of a python for-loop 
    to be run as a SLURM-job script on cineca Systems (Tested only on g100).

    Args:
        - loop (str): The path to the file containing the for loop code or the string containing the code itself.
        
        - path (str): The directory where the generated files will be saved.
        
        - chunks (int, optional): The number of chunks to divide the loop iterations into. Defaults to 2.
        
        - chunk_size (int, optional): The number of iterations per chunk. 
          If not specified, it will be calculated based on the total number of iterations and the number of chunks. 
          Defaults to None.
        
        - job (str, optional): The name of the SLURM job script. Defaults to "slurm_job".
        
        - modules (list, optional): A list of additional modules to import in the generated script. Defaults to [].
        
        - alias (list, optional): A list of aliases for the imported modules. 
          Must have the same length as the 'modules' list. Defaults to [].
        
        - run (bool, optional): Whether to run the generated SLURM job script immediately. Defaults to False.
        
        - add_time (bool, optional): Whether to append the current timestamp to the job script name. Defaults to False.
        
        - printf (bool, optional): Whether to print the paths of the generated files. Defaults to False.
        
        - filename (str, optional): The name of the SLURM job script file. Defaults to "run_slurm.bat".

        - nodes (int, optional): The number of nodes. Defaults to 1.

        - ntasks (int, optional): The number of tasks. Defaults to 1.

        - ncpus (int, optional): The number of CPUs per task. Defaults to 1.

        - mem (int, optional): The memory in MB. Defaults to 50000.

        - time (str, optional): The time limit for the job. Defaults to "1:00:00".

        - out (str, optional): The path to the output file. Defaults to "logs/job.out".

        - err (str, optional): The path to the error file. Defaults to "logs/job.err".

        - account (str, optional): The account to be used. Defaults to "IscrC_GPS-MAST".

        - partition (str, optional): The partition to be used. Defaults to "g100_usr_prod".

        - mail_type (str, optional): The type of email notifications. Defaults to "ALL".

        - mail_user (str, optional): The email address to receive notifications. Defaults to "

        - other_lines (str, optional): Other lines to be added to the SLURM job script. Defaults to ''.

        - ifor (int, optional): The index of the for loop to parallelize. Defaults to 0.

        - readme_file_name (str, optional): The name of the README file. Defaults to "README_2_RUN".

    Returns:
        - A tuple containing the paths of the generated SLURM job script, 
          the modified loop file, and the SLURM command to run the job.
    """

    # Check if the directory specified by 'path' exists
    if os.path.exists( path ) == False :
        # If not, create the directory
        os.makedirs( path, exist_ok=True )

    # 'path' is assumed to be the directory where you want to check/copy the file
    path_file = os.path.join(path, os.path.basename(loop))

    # Check if the file exists at the given path
    if os.path.isfile(loop):
        # Open the file and read its content
        with open(loop, "r") as fl:
            loop_content = fl.read()

        # Check if the file exists in the destination path
        if os.path.isfile(path_file):
            # Open the file and read its content
            with open(path_file, "r") as fl:
                path_file_content = fl.read()

            # If the content of the two files is different, copy the file to the destination path
            if loop_content != path_file_content:
                shutil.copy2(loop, path)  # Overwrite file in path if content is different
        else:
            # If the file does not exist in the destination path, copy it there
            shutil.copy2(loop, path)  # Copy file to path if it does not exist there

    # Create a the file name for the python job file
    if '.' not in filename :
        filename = filename + ".bat"
    job = filename.split(".")[0]

    # Create an empty dictionary to store the local variables of the exec function
    scope = {}

    # If add_time is True, append the current time to the job name
    if add_time == True :
        job = job + "_" + Time.strftime('%y_%m_%d_%H_%M_%S') + ".py" 
    else :
        job = job + ".py"

    # Open a new file in write mode
    f = open( path +s+ job, "w" )
    # Split the loop content by the word "import"
    imports = loop.split("import")

    import_lines = []
    # If there are imports in the loop content
    if len( imports ) > 1 :
        # For each import statement
        for i in range(1, len( imports )) :
            # Write the import statement to the new file
            f.write( f"import {imports[i].split()[0]}" )
            # Add the import statement to the list of import lines
            import_lines.append( f"import {imports[i].split()[0]}" )
            # If the import statement has an alias
            if ( len( imports[i].split() ) > 2 ) and ( imports[i].split()[1] == "as" ) :
                # Write the alias to the new file
                f.write( f" as {imports[i].split()[2]}" )
                # Add the alias to the last import line in the list
                import_lines[-1] = import_lines[-1] + f" as {imports[i].split()[2]}"
                exec( import_lines[-1], scope )
            # Write a newline character to the new file
            f.write("\n")
    
    # For each import line
    import_argparse = False
    import_os = False
    import_sys = False
    for im in import_lines :
        # If the import line imports the argparse module
        if "import argparse" in im :
            import_argparse = True
        # If the import line imports the os module
        if "import os" in im :
            import_os = True
        # If the import line imports the sys module
        if "import sys" in im :
            import_sys = True
    # If the argparse module is not imported
    if import_argparse == False :
        # Write an import statement for the argparse module to the new file
        import_lines.append( "import argparse" )
        exec( import_lines[-1], scope )
        f.write("import argparse\n")
    # If the os module is not imported
    if import_os == False :
        # Write an import statement for the os module to the new file
        import_lines.append( "import os" )
        exec( import_lines[-1], scope )
        f.write("import os\n")
    # If the sys module is not imported
    if import_sys == False :
        # Write an import statement for the sys module to the new file
        import_lines.append( "import sys" )
        exec( import_lines[-1], scope )
        f.write("import sys\n")
    
    # If there are modules to be imported
    if modules != [] :
        # For each module
        for module in modules :
            # Write an import statement for the module to the new file
            line_import = f"import {module}"
            # If there are aliases for the modules
            if alias != [] :
                # If the current module has an alias
                if modules.index( module ) in range( len( alias ) ) :
                    # Write the alias to the new file
                    line_import = line_import + f" as {alias[modules.index( module )]}"
            # Write the import statement to the new file
            import_lines.append( line_import )
            exec( import_lines[-1], scope )
            f.write( line_import + "\n")
            # Write a newline character to the new file
            f.write("\n")
    
    # Split the loop content by newline characters
    loop_lines = loop.split("\n")

    # Write the if __name__ == '__main__' statement to the new file
    f.write("\n\nif __name__ == '__main__' :\n\n")
    # Write the creation of the argparse.ArgumentParser object to the new file
    f.write("    p = argparse.ArgumentParser()\n")
    # Write the addition of the imin and imax arguments to the new file
    f.write("    p.add_argument('-imin', '--imin', type=int)\n")
    f.write("    p.add_argument('-imax', '--imax', type=int)\n")
    # Write the parsing of the arguments to the new file
    f.write("    arg = p.parse_args()\n\n")

    # Initialize the length of the iterable object in the for loop to None
    loop_len = None
    # Initialize the for loop counter to -1
    fi = -1
    # For each line in the loop content
    for line in loop_lines:
        # If the line is a for loop statement and the for loop has not started yet
        if ( line.strip().startswith("for ") ) :
            fi += 1
            if fi == ifor :
                # Get the iterable object in the for loop statement
                iter_object = line.split(" in ")[1].split(':')[0].strip()
                # Execute the iterable object to get its actual value
                iter_value = eval( iter_object, scope )
                # Get the length of the iterable object
                loop_len = len(iter_value)
                # Replace the iterable object in the for loop statement with a slice of itself
                line = line.split(" in ")[0]+' in '+ iter_object + '[ arg.imin : arg.imax ] :'

        # If we are not inside a loop
        elif line.startswith(' ') == False :
            # Execute the line
            exec( line, scope )

        # Write the line to the new file
        f.write( "    " + line + "\n" )

    # Close the new file
    f.close()

    # If the chunk size is not specified
    if chunk_size is None:
        # If the number of chunks is specified and is greater than 1
        if chunks is not None and chunks > 1:
            # Calculate the chunk size
            chunk_size = int( np.ceil( loop_len / chunks ) )
        else:
            # Raise a ValueError
            raise ValueError("The number of chunks must be greater than 1" +
                            " if chunk_size is not specified.")
    else:
        # Calculate the number of chunks
        chunks = int( np.ceil( loop_len / chunk_size ) )

    # Create a list to store the main part of the slurm script
    slurm_main_lst = []
    # Add the calculation of the task ID to the list
    slurm_main_lst.append( f'n=$SLURM_ARRAY_TASK_ID' )
    # Add the calculation of the start index of the slice to the list
    slurm_main_lst.append( f'((n=n*{chunk_size}))' )
    # Add the calculation of the end index of the slice to the list
    slurm_main_lst.append( f'((imin=n-{chunk_size}))' )
    # Add the calculation of the end index of the slice to the list
    slurm_main_lst.append( f'((imax=n+1))' )
    # Add the source command to the list
    slurm_main_lst.append( f'source $HOME/.bashrc' )
    # Add the module commands to the list
    slurm_main_lst.append( f'conda activate {sys.prefix}' )
    # Add the command to run the new file to the list
    slurm_main_lst.append( f'python {job} -imin $imin -imax $imax' )
    
    # Create a string to store the main part of the slurm script
    slurm_main_str = ""
    # For each line in the list
    for line in slurm_main_lst :
        # Add the line to the string
        slurm_main_str = slurm_main_str + line + "\n"

    # If printf is True
    if printf == True :
        print( "\n# ---------------------------------------------------------" )
        # Print the path of the new file
        print( path +s+ job )
        print( "CONTENT :\n" )
        # Print the content of the new file
        print_file( path +s+ job )

    # Create the slurm script file
    _ = create_sbatch_file( path=path, 
                            filename=filename, 
                            job=slurm_main_str, 
                            printf=printf,
                            nodes=nodes, 
                            ntasks=ntasks, 
                            ncpus=ncpus, 
                            mem=mem, 
                            time=time, 
                            out=out, 
                            err=err, 
                            account=account,
                            partition=partition,
                            mail_type=mail_type,
                            mail_user=mail_user,
                            other_lines=other_lines )

    # Create the command to submit the slurm script
    sbatch_cmd = f"sbatch --array=1-{chunks} {path+os.sep+filename} &> log &"

    # Create a README file in the directory
    with open( path +s+ readme_file_name, "w") as f :
        f.write( "# Youcan run the job by executing the following command:\n" )
        f.write( f"sbatch --array=1-{chunks} {path+os.sep+filename}\n" )
    f.close()

    # If run is True
    if run == True :
        # Submit the slurm script
        os.system( sbatch_cmd )

    # Return the path of the slurm script, the path of the new file, and the command to submit the slurm script
    return path+s+filename, path+s+job, sbatch_cmd

# -----------------------------------------------------------------------------
def script2slurm( pycode, 
                  path, 
                  modules=[], 
                  alias=[], 
                  run=False, 
                  add_time=False,
                  printf=False, 
                  filename="run_slurm.bat",
                  nodes=1, 
                  ntasks=1, 
                  ncpus=1, 
                  mem=50000, 
                  time="1:00:00", 
                  out= "logs/job.out", 
                  err= "logs/job.err", 
                  account="OGS23_PRACE_IT",
                  partition="g100_usr_prod",
                  mail_type="ALL",
                  mail_user="lzampa@ogs.it",
                  other_lines='', 
                  readme_file_name="README_2_RUN",
                  absolute_path=False ) :
    
    """
    Generate a simple parallelized version of a python for-loop 
    to be run as a SLURM-job script on cineca Systems (Tested only on g100).

    Args:
        - pycode (str): 
        
        - path (str): The directory where the generated files will be saved.
        
        - chunks (int, optional): The number of chunks to divide the loop iterations into. Defaults to 2.
        
        - chunk_size (int, optional): The number of iterations per chunk. 
          If not specified, it will be calculated based on the total number of iterations and the number of chunks. 
          Defaults to None.
        
        - job (str, optional): The name of the SLURM job script. Defaults to "slurm_job".
        
        - modules (list, optional): A list of additional modules to import in the generated script. Defaults to [].
        
        - alias (list, optional): A list of aliases for the imported modules. 
          Must have the same length as the 'modules' list. Defaults to [].
        
        - run (bool, optional): Whether to run the generated SLURM job script immediately. Defaults to False.
        
        - add_time (bool, optional): Whether to append the current timestamp to the job script name. Defaults to False.
        
        - printf (bool, optional): Whether to print the paths of the generated files. Defaults to False.
        
        - filename (str, optional): The name of the SLURM job script file. Defaults to "run_slurm.bat".

        - nodes (int, optional): The number of nodes. Defaults to 1.

        - ntasks (int, optional): The number of tasks. Defaults to 1.

        - ncpus (int, optional): The number of CPUs per task. Defaults to 1.

        - mem (int, optional): The memory in MB. Defaults to 50000.

        - time (str, optional): The time limit for the job. Defaults to "1:00:00".

        - out (str, optional): The path to the output file. Defaults to "logs/job.out".

        - err (str, optional): The path to the error file. Defaults to "logs/job.err".

        - account (str, optional): The account to be used. Defaults to "IscrC_GPS-MAST".

        - partition (str, optional): The partition to be used. Defaults to "g100_usr_prod".

        - mail_type (str, optional): The type of email notifications. Defaults to "ALL".

        - mail_user (str, optional): The email address to receive notifications. Defaults to "

        - other_lines (str, optional): Other lines to be added to the SLURM job script. Defaults to ''.

        - readme_file_name (str, optional): The name of the README file. Defaults to "README_2_RUN".

    Returns:
        - A tuple containing the paths of the generated SLURM job script, 
          the modified loop file, and the SLURM command to run the job.
    """

    # Check if the directory specified by 'path' exists
    if os.path.exists( path ) == False :
        # If not, create the directory
        os.makedirs( path, exist_ok=True )

    # 'path' is assumed to be the directory where you want to check/copy the file
    path_file = os.path.join(path, os.path.basename(pycode))

    # Check if the file exists at the given path
    if os.path.isfile(pycode):
        # Open the file and read its content
        with open(pycode, "r") as fl:
            loop_content = fl.read()

        # Check if the file exists in the destination path
        if os.path.isfile(path_file):
            # Open the file and read its content
            with open(path_file, "r") as fl:
                path_file_content = fl.read()

            # If the content of the two files is different, copy the file to the destination path
            if loop_content != path_file_content:
                shutil.copy2(pycode, path)  # Overwrite file in path if content is different
        else:
            # If the file does not exist in the destination path, copy it there
            shutil.copy2(pycode, path)  # Copy file to path if it does not exist there

    # Create a the file name for the python job file
    if '.' not in filename :
        filename = filename + ".bat"
    job = filename.split(".")[0]

    # Create an empty dictionary to store the local variables of the exec function
    scope = {}

    # If add_time is True, append the current time to the job name
    if add_time == True :
        job = job + "_" + Time.strftime('%y_%m_%d_%H_%M_%S') + ".py" 
    else :
        job = job + ".py"

    # Open a new file in write mode
    pyjob_file = path +s+ job
    f = open( pyjob_file, "w" )
    # Split the loop content by the word "import"
    imports = pycode.split("import")

    import_lines = []
    # If there are imports in the code
    if len( imports ) > 1 :
        # For each import statement
        for i in range(1, len( imports )) :
            # Write the import statement to the new file
            f.write( f"import {imports[i].split()[0]}" )
            # Add the import statement to the list of import lines
            import_lines.append( f"import {imports[i].split()[0]}" )
            # If the import statement has an alias
            if ( len( imports[i].split() ) > 2 ) and ( imports[i].split()[1] == "as" ) :
                # Write the alias to the new file
                f.write( f" as {imports[i].split()[2]}" )
                # Add the alias to the last import line in the list
                import_lines[-1] = import_lines[-1] + f" as {imports[i].split()[2]}"
                exec( import_lines[-1], scope )
            # Write a newline character to the new file
            f.write("\n")
    
    # For each import line
    import_argparse = False
    import_os = False
    import_sys = False
    for im in import_lines :
        # If the import line imports the argparse module
        if "import argparse" in im :
            import_argparse = True
        # If the import line imports the os module
        if "import os" in im :
            import_os = True
        # If the import line imports the sys module
        if "import sys" in im :
            import_sys = True
    # If the argparse module is not imported
    if import_argparse == False :
        # Write an import statement for the argparse module to the new file
        import_lines.append( "import argparse" )
        exec( import_lines[-1], scope )
        f.write("import argparse\n")
    # If the os module is not imported
    if import_os == False :
        # Write an import statement for the os module to the new file
        import_lines.append( "import os" )
        exec( import_lines[-1], scope )
        f.write("import os\n")
    # If the sys module is not imported
    if import_sys == False :
        # Write an import statement for the sys module to the new file
        import_lines.append( "import sys" )
        exec( import_lines[-1], scope )
        f.write("import sys\n")
    
    # If there are other input modules to be imported
    if modules != [] :
        # For each module
        for module in modules :
            # Write an import statement for the module to the new file
            line_import = f"import {module}"
            # If there are aliases for the modules
            if alias != [] :
                # If the current module has an alias
                if modules.index( module ) in range( len( alias ) ) :
                    # Write the alias to the new file
                    line_import = line_import + f" as {alias[modules.index( module )]}"
            # Write the import statement to the new file
            import_lines.append( line_import )
            exec( import_lines[-1], scope )
            f.write( line_import + "\n")
            # Write a newline character to the new file
            f.write("\n")
    
    # Split the code
    code_lines = pycode.split("\n")

    for line in code_lines:

        if 'import' in line:
            continue
        f.write( line + "\n" )

    # Close the new file
    f.close()

    # Create a list to store the main part of the slurm script
    slurm_main_lst = []
    # Add the source command to the list
    slurm_main_lst.append( f'source $HOME/.bashrc' )
    # Add the module commands to the list
    slurm_main_lst.append( f'conda activate {sys.prefix}' )
    # Add the command to run the new file to the list
    if absolute_path == True :
        slurm_main_lst.append( f'python {path +s+ job}' )
    else :
        slurm_main_lst.append( f'python {job}' )
    # Create a string to store the main part of the slurm script
    slurm_main_str = ""
    # For each line in the list
    for line in slurm_main_lst :
        # Add the line to the string
        slurm_main_str = slurm_main_str + line + "\n"

    # If printf is True
    if printf == True :
        print( "\n# ---------------------------------------------------------" )
        # Print the path of the new file
        print( path +s+ job )
        print( "CONTENT :\n" )
        # Print the content of the new file
        print_file( path +s+ job )

    # Check if you are in the Cineca system
    if is_cineca_system() :

        # Create the slurm script file
        _ = create_sbatch_file( path=path, 
                                filename=filename, 
                                job=slurm_main_str, 
                                printf=printf,
                                nodes=nodes, 
                                ntasks=ntasks, 
                                ncpus=ncpus, 
                                mem=mem, 
                                time=time, 
                                out=out, 
                                err=err, 
                                account=account,
                                partition=partition,
                                mail_type=mail_type,
                                mail_user=mail_user,
                                other_lines=other_lines )

        # If you are in the Cineca system, create the command to submit the slurm script
        cmd = f"sbatch {path+os.sep+filename} &> log &"
    
    # If you are not in the Cineca system (e.g., you are testing the script locally)
    else :
        # Check how many cpus are available
        n_cpus = os.cpu_count()

        # If the number of cpus is greater than 1
        if n_cpus > 1:
            # Wait until at least one CPU is free
            while True:
                cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
                if any( usage < 100 for usage in cpu_usage ):
                    break
                time.sleep(1)  # Wait for 1 second before checking again

            # Write command line that : 
            # 1) ensure conda is properly initialized 
            # 2) activate the proper environment 
            # 3) run the python job
            conda_init = "source $(conda info --base)/etc/profile.d/conda.sh"
            cmd = f"bash -c '{conda_init} && conda activate {sys.prefix} && python {path+os.sep+job}' &"
            print( f"\n\t{cmd}" )

    with open( path +s+ readme_file_name, "w") as f :
        f.write( "# Youcan run the job by executing the following command:\n" )
        f.write( f"{cmd}" )

    # If run is True
    if run == True :
        # Submit the slurm script
        os.system( cmd )

    # Return the path of the slurm script, the path of the new file, 
    # and the command to submit the slurm script
    return path+s+filename, path+s+job, cmd

