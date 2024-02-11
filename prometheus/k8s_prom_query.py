

class K8sPromQueryInstance:
    def __init__(self, cluster_info):
        self.tidb_instance_query = '''
            kube_node_labels{tenant="%s",label_cluster="%s",label_component="tidb"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])

        self.tikv_instance_query = '''
             kube_node_labels{tenant="%s",label_cluster="%s",label_component="tikv"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])

        self.pd_instance_query = '''
             kube_node_labels{tenant="%s",label_cluster="%s",label_component="pd"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])

        self.tiflash_instance_query = '''
             kube_node_labels{tenant="%s",label_cluster="%s",label_component="tiflash"}
        ''' % (cluster_info['tenant_id'], cluster_info['cluster_id'])


class K8sPromQueryInstanceMetrics:
    def __init__(self, cluster_info, instance_name):
        self.instance_disk_iops_query = '''
            sum(rate(node_disk_writes_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance) + 
            sum(rate(node_disk_reads_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name, cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)

        self.instance_disk_bandwidth_query = '''
            sum(rate(node_disk_read_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance) + 
            sum(rate(node_disk_written_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[2m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name, cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)

        self.instance_network_received_query = '''
            sum(rate(node_network_receive_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)

        self.instance_network_transmitted_query = '''
            sum(rate(node_network_transmit_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance="%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instance_name)


class K8sPromQueryBatchInstanceMetrics:
    def __init__(self, cluster_info, instances):
        self.batch_instance_disk_iops_query = '''
             sum(rate(node_disk_writes_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance) + 
             sum(rate(node_disk_reads_completed_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance)
         ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances, cluster_info['tenant_id'],
                cluster_info['k8s_cluster'], instances)

        self.batch_instance_disk_bandwidth_query = '''
            sum(rate(node_disk_read_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance) + 
            sum(rate(node_disk_written_bytes_total{tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[2m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances, cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances)

        self.batch_instance_network_received_query = '''
            sum(rate(node_network_receive_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances)

        self.batch_instance_network_transmitted_query = '''
            sum(rate(node_network_transmit_bytes_total{job="node-exporter", tenant="%s", k8s_cluster_info=~"%s", instance=~"%s"}[1m])) by (instance)
        ''' % (cluster_info['tenant_id'], cluster_info['k8s_cluster'], instances)

