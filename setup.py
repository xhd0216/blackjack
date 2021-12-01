import setuptools

setuptools.setup(
    name="blackjack",
    version="0.1.0",
    author="Joe Awake",
    author_email="xhd0216@gmail.com",
    description="blackjack frontend",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'cryptography',
        'PyJWT',
        'trendlines',
    ],
)
