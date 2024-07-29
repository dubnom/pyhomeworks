rm dist/*
python3 setup.py sdist bdist_wheel
twine upload dist/*
sleep 10 
pip install --upgrade pyhomeworks
cd pyhomeworks

