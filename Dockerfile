FROM continuumio/miniconda3
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y build-essential  && \
    apt-get install -y wget && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/Raster-Viz/Raster-Viz.git

WORKDIR /Raster-Viz
RUN cd /Raster-Viz
RUN rmdir raster_tools
RUN git rm --cached raster_tools
RUN git submodule add https://github.com/Raster-Viz/raster_tools.git
SHELL ["/bin/bash", "-c"]
WORKDIR /Raster-Viz/raster_tools
RUN conda env create -f ./requirements/dev.yml 
RUN conda init bash
SHELL ["conda", "run", "-n", "rstools", "/bin/bash", "-c"]
RUN SITE_PACKAGES=$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")
RUN echo -e "$(pwd)\n." > "${SITE_PACKAGES}/raster-tools.egg-link" && \
    pip install -e . && \
    rm -r raster_tools.egg-info && \
    python setup.py build_ext --inplace && \
    pre-commit install
WORKDIR /Raster-Viz
RUN conda install -c anaconda django
RUN python manage.py makemigrations
RUN python manage.py migrate
EXPOSE 8000
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "rstools", "python", "manage.py", "runserver"]






