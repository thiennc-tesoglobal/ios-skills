#!/bin/sh
set -eu

usage() {
    cat <<'EOF'
Usage: typecheck_skill_fixtures.sh stable|beta

Type-checks Apple framework fixtures against the selected Xcode lane.
  stable  Requires Xcode 26.6 and compiles the iOS 26 fixtures.
  beta    Requires Xcode 27.x and compiles stable plus iOS 27 fixtures.
EOF
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
    stable)
        expected_version="26.6"
        deployment_target="arm64-apple-ios26.0"
        fixture_directories="stable"
        ;;
    beta)
        expected_version="27."
        deployment_target="arm64-apple-ios27.0"
        fixture_directories="stable beta"
        ;;
    *)
        usage >&2
        exit 64
        ;;
esac

script_directory=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repository_root=$(CDPATH= cd -- "$script_directory/../.." && pwd)
xcode_version=$(xcodebuild -version | awk 'NR == 1 { print $2 }')

case "$xcode_version" in
    "$expected_version"*) ;;
    *)
        echo "Expected Xcode $expected_version lane, found Xcode $xcode_version" >&2
        exit 1
        ;;
esac

sdk_path=$(xcrun --sdk iphoneos --show-sdk-path)

for fixture_directory in $fixture_directories; do
    find "$repository_root/.github/compile-fixtures/$fixture_directory" -name '*.swift' -type f -print |
        sort |
        while IFS= read -r fixture; do
            echo "Type-checking ${fixture#"$repository_root/"}"
            xcrun swiftc \
                -typecheck \
                -warnings-as-errors \
                -strict-concurrency=complete \
                -swift-version 6 \
                -sdk "$sdk_path" \
                -target "$deployment_target" \
                "$fixture"
        done
done
