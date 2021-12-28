#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
import argparse

from pipeline.backend.pipeline import PipeLine
from pipeline.utils.tools import load_job_config

def main(role="guest", config="../../config.yaml", namespace=""):
    # obtain config
    if isinstance(config, str):
        config = load_job_config(config)

    parties = config.parties
    data_base = config.data_base_dir

    # partition for data storage
    partition = 4

    # party id
    if role == "guest":
        party_id = parties.guest[0]
    elif role == "host":
        party_id = parties.host[0]
    else:
        print("Invalid role %s" % role)
        exit()

    # table name and namespace, used in FATE job configuration
    breast_homo_data = {"name": "breast_homo_%s" % role, "namespace": f"experiment{namespace}"}
    breast_hetero_data = {"name": "breast_hetero_%s" % role, "namespace": f"experiment{namespace}"}
    vehicle_homo_data = {"name": "vehicle_scale_homo_%s" % role, "namespace": f"experiment{namespace}"}
    vehicle_hetero_data = {"name": "vehicle_scale_hetero_%s" % role, "namespace": f"experiment{namespace}"}

    pipeline_upload = PipeLine().set_initiator(role=role, party_id=party_id)

    if role == "guest":
        pipeline_upload = pipeline_upload.set_roles(guest=party_id)
    elif role == "host":
        pipeline_upload = pipeline_upload.set_roles(host=party_id)
    else:
        print("Invalid role %s" % role)
        exit()

    # add upload dataset info and path to csv file(s) to be uploaded
    pipeline_upload.add_upload_data(file=os.path.join(data_base, "examples/data/breast_homo_%s.csv" % role),
                                    table_name=breast_homo_data["name"],
                                    namespace=breast_homo_data["namespace"],
                                    head=1, partition=partition,
                                    id_delimiter=",")

    pipeline_upload.add_upload_data(file=os.path.join(data_base, "examples/data/breast_hetero_%s.csv" % role),
                                    table_name=breast_hetero_data["name"],
                                    namespace=breast_hetero_data["namespace"],
                                    head=1, partition=partition,
                                    id_delimiter=",")

    pipeline_upload.add_upload_data(file=os.path.join(data_base, "examples/data/vehicle_scale_homo_%s.csv" % role),
                                    table_name=vehicle_homo_data["name"],
                                    namespace=vehicle_homo_data["namespace"],
                                    head=1, partition=partition,
                                    id_delimiter=",")

    pipeline_upload.add_upload_data(file=os.path.join(data_base, "examples/data/vehicle_scale_hetero_%s.csv" % role),
                                    table_name=vehicle_hetero_data["name"],
                                    namespace=vehicle_hetero_data["namespace"],
                                    head=1, partition=partition,
                                    id_delimiter=",")

    # upload both datasets
    pipeline_upload.upload(drop=1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PIPELINE UPLOAD")
    parser.add_argument("-role", type=str,
                        help="role")
    parser.add_argument("-config", type=str,
                        help="config file")
    args = parser.parse_args()
    if args.role is not None and (args.role != "guest" and args.role != "host"):
        print("The role argument should be set to either guest or host")
        exit()
    print("Role = %s" % args.role)
    if args.role is not None and args.config is None:
        main(args.role)
    elif args.role is None and args.config is not None:
        main(args.config)
    elif args.role is not None and args.config is not None:
        main(args.role, args.config)
    else:
        main()
