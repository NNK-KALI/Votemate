from solcx import install_solc, compile_standard, set_solc_version_pragma
import json
import os

if __name__ == "__main__":
    install_solc("0.8.0")
    set_solc_version_pragma("0.8.0")
    # print("solc installed folder -> {}".format(get_solcx_install_folder()))
    # print("installed solc versions -> {}".format(get_installed_solc_versions()))
    # print("current solc version -> {}".format(get_solc_version()))

    # Read the solidity code from the Contest file
    with open(os.path.dirname(__file__) + "/" + "Contest.sol", "r") as file:
        contest_source_code = file.read()

    # Compile solidity code
    compiled_sol = compile_standard(
        {
            "language": "Solidity",
            "sources": {"Contest.sol": {"content": contest_source_code}},
            "settings": {
                "outputSelection": {
                    "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                },
            },
        },
        solc_version="0.8.0",
    )

    # write the compiled Contest code to a file
    with open(os.path.dirname(__file__) + "/" + "compiled_code.json", "w") as file:
        json.dump(compiled_sol, file)

    # Get ByteCode
    bytecode = compiled_sol["contracts"]["Contest.sol"]["Contest"]["evm"]["bytecode"][
        "object"
    ]

    # Save bytecode to file
    with open(os.path.dirname(__file__) + "/" + "bytecode.json", "w") as file:
        json.dump(bytecode, file)

    # Get ABI
    abi = compiled_sol["contracts"]["Contest.sol"]["Contest"]["abi"]

    # save ABI to file
    with open(os.path.dirname(__file__) + "/" + "ABI.json", "w") as file:
        json.dump(abi, file)
