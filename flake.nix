{
  description = "Python 3.13";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  };

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";

      pkgs = import nixpkgs {
        inherit system;
        config = {
          allowUnfree = true;
          cudaSupport = true;
        };
      };

      runtimeLibs = with pkgs; [
        stdenv.cc.cc.lib
        libGL
        glib
        zlib
        cudaPackages.cudatoolkit
        cudaPackages.cudnn
        linuxPackages.nvidia_x11
      ];

    in {
      devShells.${system}.default = pkgs.mkShell {
        name = "shell";

        packages = with pkgs; [
          python313
          python313Packages.pip
          python313Packages.virtualenv
        ];

        buildInputs = runtimeLibs;

        shellHook = ''
          export LD_LIBRARY_PATH="${pkgs.lib.makeLibraryPath runtimeLibs}:$LD_LIBRARY_PATH"
          export CUDA_PATH=${pkgs.cudaPackages.cudatoolkit}

          if [ ! -d "env" ]; then
            python -m venv env
          fi

          export UV_PROJECT_ENVIRONMENT=env

          source env/bin/activate
        '';
      };
    };
}
